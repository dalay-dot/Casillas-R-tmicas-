from pathlib import Path
import pygame


class Musica:
    def __init__(self):
        self.carpeta = Path(__file__).resolve().parent / "canciones"
        self.carpeta.mkdir(exist_ok=True)

        self.canciones = []
        self.indice = 0
        self.volumen = 0.5
        self.silenciada = False
        self.disponible = False
        self.error = ""

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()

            self.disponible = True
            pygame.mixer.music.set_volume(self.volumen)

        except pygame.error:
            self.error = "Audio no disponible"

        self.actualizar_lista()

    def actualizar_lista(self):
        extensiones = {".mp4", ".ogg", ".wav"}

        self.canciones = sorted(
            [
                archivo
                for archivo in self.carpeta.iterdir()
                if archivo.is_file()
                and archivo.suffix.lower() in extensiones
            ],
            key=lambda archivo: archivo.name.lower(),
        )

        if self.canciones:
            self.indice %= len(self.canciones)
        else:
            self.indice = 0

    def nombre_actual(self):
        if not self.disponible:
            return "Audio no disponible"

        if not self.canciones:
            return "Sin canciones"

        return self.canciones[self.indice].stem

    def cambiar(self, direccion):
        if self.canciones:
            self.indice = (
                self.indice + direccion
            ) % len(self.canciones)

    def reproducir(self):
        if not self.disponible or not self.canciones:
            return

        try:
            ruta = self.canciones[self.indice]
            pygame.mixer.music.load(str(ruta))
            pygame.mixer.music.play(-1)
            self.error = ""

        except (pygame.error, OSError):
            self.error = "No se pudo abrir la canción"

    def detener(self):
        if self.disponible:
            pygame.mixer.music.stop()

    def ajustar_volumen(self, cambio):
        self.volumen = max(
            0.0,
            min(1.0, self.volumen + cambio),
        )
        self.aplicar_volumen()

    def alternar_silencio(self):
        self.silenciada = not self.silenciada
        self.aplicar_volumen()

    def aplicar_volumen(self):
        if self.disponible:
            volumen_final = 0 if self.silenciada else self.volumen
            pygame.mixer.music.set_volume(volumen_final)