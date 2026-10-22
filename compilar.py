import os
import subprocess
import sys
from pathlib import Path


def compilar():
    base_dir = Path(__file__).resolve().parent
    icono_path = base_dir / "icono.ico"
    canciones_path = base_dir / "canciones"

    print("=" * 60)
    print(" INICIANDO COMPILACIÓN DE CASILLAS RÍTMICAS ")
    print("=" * 60)

    # Comando PyInstaller
    comando = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=CasillasRitmicas",
        f"--add-data={canciones_path};canciones",
    ]

    if icono_path.exists():
        comando.append(f"--icon={icono_path}")

    comando.append(str(base_dir / "main.py"))

    print(f"Ejecutando: {' '.join(comando)}")
    resultado = subprocess.run(comando, cwd=str(base_dir))

    if resultado.returncode == 0:
        exe_path = base_dir / "dist" / "CasillasRitmicas.exe"
        print("\n" + "=" * 60)
        print(" ¡COMPILACIÓN EXITOSA!")
        print(f" Ejecutable generado en: {exe_path}")
        print(" Puedes compartir la carpeta 'dist' o comprimirla en un .ZIP")
        print(" para que tus amigos jueguen con solo hacer doble clic.")
        print("=" * 60 + "\n")
    else:
        print(f"\n[ERROR] La compilación falló con código {resultado.returncode}")


if __name__ == "__main__":
    compilar()
