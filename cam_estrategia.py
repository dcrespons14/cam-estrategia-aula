"""Public helper imported by the short Colab access cell."""
import getpass
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile


def desbloquear_cuaderno():
    endpoint = "https://cam-estrategia-aula.david-simracing14.chatgpt.site/api/materials"
    password = getpass.getpass("Contraseña del curso: ")
    request = urllib.request.Request(
        endpoint, data=json.dumps({"password": password}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    del password
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            archive = response.read(10 * 1024 * 1024 + 1)
            expected_hash = response.headers.get("X-Course-SHA256")
    except urllib.error.HTTPError as error:
        if error.code == 401:
            raise RuntimeError("Contraseña incorrecta. Vuelve a ejecutar esta celda.") from None
        if error.code == 429:
            raise RuntimeError("Demasiados intentos. Espera 15 minutos y vuelve a probar.") from None
        raise RuntimeError("El acceso al curso no está disponible. Inténtalo más tarde.") from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError("No se pudo conectar. Comprueba la conexión y vuelve a ejecutar la celda.") from None
    finally:
        request.data = None
    if len(archive) > 10 * 1024 * 1024 or not expected_hash or hashlib.sha256(archive).hexdigest() != expected_hash:
        raise RuntimeError("La descarga no es válida. Vuelve a ejecutar la celda.")
    destination = Path.cwd() / "curso-motorsport"
    if destination.exists():
        print("Se conserva tu carpeta curso-motorsport y sus modificaciones.")
    else:
        with zipfile.ZipFile(io.BytesIO(archive)) as package:
            for item in package.infolist():
                target = (Path.cwd() / item.filename).resolve()
                if not target.is_relative_to(destination.resolve()):
                    raise RuntimeError("El archivo contiene una ruta no válida.")
            with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
                package.extractall(temporary)
                (Path(temporary) / "curso-motorsport").rename(destination)
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
