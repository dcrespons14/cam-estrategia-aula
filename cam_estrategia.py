"""Public helper imported by the short Colab access cell."""
import base64
import getpass
import os
from pathlib import Path
import subprocess
import sys


def desbloquear_cuaderno():
    destination = Path.cwd() / "curso-motorsport"
    if destination.exists():
        print("Se conserva tu carpeta curso-motorsport y sus modificaciones.")
    else:
        password = getpass.getpass("Contraseña del curso: ")
        credentials = base64.b64encode(("alumno:" + password).encode("utf-8")).decode("ascii")
        del password
        # La contraseña va en una cabecera pasada por el entorno: no queda en la URL,
        # en la configuración del repositorio ni en la lista de procesos.
        environment = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_CONFIG_COUNT="2",
                           GIT_CONFIG_KEY_0="http.extraHeader",
                           GIT_CONFIG_VALUE_0="Authorization: Basic " + credentials,
                           GIT_CONFIG_KEY_1="credential.helper", GIT_CONFIG_VALUE_1="")
        del credentials
        result = subprocess.run(
            ["git", "clone", "--quiet", "https://cam-estrategia-aula.cam-estrategia.workers.dev/cam-estrategia.git", str(destination)],
            env=environment, capture_output=True, text=True,
        )
        if result.returncode != 0:
            message = result.stderr
            if "429" in message:
                raise RuntimeError("Demasiados intentos. Espera 15 minutos y vuelve a probar.")
            if "401" in message or "Authentication failed" in message or "terminal prompts disabled" in message:
                raise RuntimeError("Contraseña incorrecta. Vuelve a ejecutar esta celda.")
            if "Could not resolve host" in message or "Failed to connect" in message:
                raise RuntimeError("No se pudo conectar. Comprueba la conexión y vuelve a ejecutar la celda.")
            raise RuntimeError("El acceso al curso no está disponible. Inténtalo más tarde.")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "-e", str(destination)], check=True,
    )
    source = str(destination / "src")
    if source not in sys.path:
        sys.path.insert(0, source)
    print("Acceso correcto. Ya puedes ejecutar los ejercicios.")
    print("Código y notebooks: " + str(destination))


if __name__ == "__main__":
    desbloquear_cuaderno()
