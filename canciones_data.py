import os
from pathlib import Path


class Cancion:
    def __init__(self, id_cancion, titulo, artista, bpm, dificultad, estrellas, notas=None, ruta_audio=None):
        self.id = id_cancion
        self.titulo = titulo
        self.artista = artista
        self.bpm = bpm
        self.dificultad = dificultad  # 'Fácil', 'Normal', 'Difícil', 'Extremo'
        self.estrellas = estrellas
        self.notas = notas or []  # lista de tuplas: (tiempo_seg, carril, nota_piano, es_sostenida, duracion)
        self.ruta_audio = ruta_audio

    @property
    def duracion_total(self):
        if not self.notas:
            return 60.0
        ultima = max(t + (dur if sost else 0.5) for t, c, n, sost, dur in self.notas)
        return round(ultima + 2.0, 1)


def generar_patron_fur_elise():
    """Genera el beatmap icónico de Für Elise de Beethoven."""
    # Notas: E5, D#5, E5, D#5, E5, B4, D5, C5, A4 ...
    bpm = 135
    t_negra = 60.0 / bpm
    t_corchea = t_negra / 2.0

    melodia = [
        # (nota, carril, duracion_en_corcheas)
        ("E5", 3, 1), ("D#5", 2, 1), ("E5", 3, 1), ("D#5", 2, 1), ("E5", 3, 1),
        ("B4", 2, 1), ("D5", 3, 1), ("C5", 2, 1), ("A4", 1, 2),
        ("C4", 0, 1), ("E4", 1, 1), ("A4", 1, 1), ("B4", 2, 2),
        ("E4", 1, 1), ("G#4", 2, 1), ("B4", 2, 1), ("C5", 3, 2),
        # Repetición con variación
        ("E5", 3, 1), ("D#5", 2, 1), ("E5", 3, 1), ("D#5", 2, 1), ("E5", 3, 1),
        ("B4", 2, 1), ("D5", 3, 1), ("C5", 2, 1), ("A4", 1, 2),
        ("C4", 0, 1), ("E4", 1, 1), ("A4", 1, 1), ("B4", 2, 2),
        ("E4", 1, 1), ("C5", 3, 1), ("B4", 2, 1), ("A4", 1, 3),
        # Segunda sección rápida
        ("B4", 2, 1), ("C5", 3, 1), ("D5", 3, 1), ("E5", 3, 2),
        ("G4", 1, 1), ("F5", 3, 1), ("E5", 3, 1), ("D5", 2, 2),
        ("F4", 0, 1), ("E5", 3, 1), ("D5", 2, 1), ("C5", 2, 2),
        ("E4", 1, 1), ("D5", 2, 1), ("C5", 2, 1), ("B4", 1, 3),
    ]

    notas = []
    t_actual = 1.0  # Segundo inicial de margen
    for nota, carril, corcheas in melodia:
        dur = corcheas * t_corchea
        es_sostenida = corcheas >= 3
        longitud = 140 if es_sostenida else 0
        notas.append((round(t_actual, 3), carril, nota, es_sostenida, longitud))
        t_actual += dur

    return notas


def generar_patron_canon_in_d():
    """Genera el beatmap armónico de Canon in D de Pachelbel."""
    bpm = 120
    t_negra = 60.0 / bpm
    secuencia = [
        ("D4", 0, 2), ("A4", 2, 2), ("B4", 2, 2), ("F#4", 1, 2),
        ("G4", 1, 2), ("D4", 0, 2), ("G4", 1, 2), ("A4", 2, 2),
        # Arpegios más rápidos
        ("D5", 3, 1), ("F#4", 1, 1), ("A4", 2, 1), ("D5", 3, 1),
        ("C#5", 3, 1), ("E4", 0, 1), ("A4", 2, 1), ("C#5", 3, 1),
        ("B4", 2, 1), ("D4", 0, 1), ("F#4", 1, 1), ("B4", 2, 1),
        ("A4", 2, 1), ("C#4", 0, 1), ("E4", 1, 1), ("A4", 2, 1),
        ("G4", 1, 1), ("B3", 0, 1), ("D4", 1, 1), ("G4", 1, 1),
        ("F#4", 1, 1), ("A3", 0, 1), ("D4", 1, 1), ("F#4", 1, 1),
        ("G4", 1, 1), ("B3", 0, 1), ("D4", 1, 1), ("G4", 1, 1),
        ("A4", 2, 1), ("C#4", 0, 1), ("E4", 1, 1), ("A4", 2, 2),
    ]

    notas = []
    t_actual = 1.0
    for nota, carril, figuras in secuencia:
        dur = figuras * (t_negra / 2.0)
        es_sost = figuras >= 2
        notas.append((round(t_actual, 3), carril, nota, es_sost, 120 if es_sost else 0))
        t_actual += dur

    return notas


def generar_patron_cyber_rush():
    """Genera un beatmap dinámico y retador de música electrónica / synthwave."""
    bpm = 145
    t_pulso = 60.0 / bpm
    notas = []
    t_actual = 1.0
    carril_previo = 0

    patron_carriles = [0, 1, 2, 3, 2, 1, 0, 2, 1, 3, 2, 0, 1, 3, 1, 2, 0, 3, 1, 2, 3, 0]
    escalas = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]

    for i in range(70):
        carril = patron_carriles[i % len(patron_carriles)]
        nota = escalas[i % len(escalas)]
        # Cada cierto tiempo meter una sostenida
        es_sost = (i % 7 == 0 and i > 0)
        notas.append((round(t_actual, 3), carril, nota, es_sost, 160 if es_sost else 0))
        t_actual += (t_pulso * 1.5 if es_sost else t_pulso * 0.75)

    return notas


class CatalogoCanciones:
    def __init__(self):
        self.canciones = []
        self.cargar_canciones_base()
        self.escanear_canciones_usuario()

    def cargar_canciones_base(self):
        # 1. Für Elise
        self.canciones.append(
            Cancion(
                id_cancion="fur_elise",
                titulo="Für Elise (Para Elisa)",
                artista="L. v. Beethoven",
                bpm=135,
                dificultad="Normal",
                estrellas=3,
                notas=generar_patron_fur_elise(),
            )
        )

        # 2. Canon in D
        self.canciones.append(
            Cancion(
                id_cancion="canon_d",
                titulo="Canon en Re Mayor",
                artista="Johann Pachelbel",
                bpm=120,
                dificultad="Fácil",
                estrellas=2,
                notas=generar_patron_canon_in_d(),
            )
        )

        # 3. Cyber Rush
        self.canciones.append(
            Cancion(
                id_cancion="cyber_rush",
                titulo="Cyber Rush (Arcade Neon)",
                artista="Original Synth",
                bpm=145,
                dificultad="Difícil",
                estrellas=4,
                notas=generar_patron_cyber_rush(),
            )
        )

    def escanear_canciones_usuario(self):
        """Escanea la carpeta 'canciones' en busca de audios MP3/WAV/OGG válidos."""
        carpeta = Path(__file__).resolve().parent / "canciones"
        carpeta.mkdir(exist_ok=True)

        formatos_validos = {".mp3", ".wav", ".ogg"}

        for archivo in carpeta.iterdir():
            if archivo.is_file() and archivo.suffix.lower() in formatos_validos:
                # Evitar archivos de 0 bytes
                if archivo.stat().st_size < 1024:
                    continue

                nombre_limpio = archivo.stem.replace("_", " ").title()
                notas_auto = self._generar_notas_para_audio_personalizado(archivo)

                self.canciones.append(
                    Cancion(
                        id_cancion=f"user_{archivo.stem}",
                        titulo=nombre_limpio[:28],
                        artista="Audio Personalizado",
                        bpm=128,
                        dificultad="Normal",
                        estrellas=3,
                        notas=notas_auto,
                        ruta_audio=archivo,
                    )
                )

    def _generar_notas_para_audio_personalizado(self, ruta_archivo):
        """Genera un patrón rítmico automático equilibrado de ~90 segundos."""
        bpm = 126
        intervalo = 60.0 / bpm
        notas = []
        t = 1.0
        patron = [0, 2, 1, 3, 2, 0, 3, 1, 2, 1, 3, 0]
        escalas = ["C4", "E4", "G4", "C5"]

        for i in range(120):
            carril = patron[i % len(patron)]
            nota = escalas[carril]
            es_sost = (i % 8 == 0)
            notas.append((round(t, 3), carril, nota, es_sost, 130 if es_sost else 0))
            t += intervalo

        return notas
