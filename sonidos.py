import math
import numpy as np
import pygame
from pathlib import Path


class MotorSonido:
    def __init__(self, gestor_datos):
        self.gestor = gestor_datos
        self.disponible = False
        self.sfx_cache = {}
        self.notas_piano = {}

        ajustes = self.gestor.datos.get("ajustes", {})
        self.vol_musica = ajustes.get("volumen_musica", 0.7)
        self.vol_sfx = ajustes.get("volumen_sfx", 0.8)
        self.silenciado = ajustes.get("silencio", False)

        try:
            if pygame.mixer.get_init() is None:
                # 44.1kHz, 16 bit estéreo con buffer pequeño para latencia casi nula
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.disponible = True
            self.aplicar_volumenes()
            self._generar_libreria_sfx()
            self._generar_banco_piano()
        except Exception as e:
            print(f"[Sonido] No se pudo inicializar audio: {e}")

    def aplicar_volumenes(self):
        if not self.disponible:
            return
        m_vol = 0.0 if self.silenciado else self.vol_musica
        s_vol = 0.0 if self.silenciado else self.vol_sfx

        pygame.mixer.music.set_volume(m_vol)
        for snd in self.sfx_cache.values():
            snd.set_volume(s_vol)
        for snd in self.notas_piano.values():
            snd.set_volume(s_vol)

    def cambiar_volumen_musica(self, delta):
        self.vol_musica = max(0.0, min(1.0, round(self.vol_musica + delta, 2)))
        self.gestor.datos["ajustes"]["volumen_musica"] = self.vol_musica
        self.gestor.guardar()
        self.aplicar_volumenes()

    def cambiar_volumen_sfx(self, delta):
        self.vol_sfx = max(0.0, min(1.0, round(self.vol_sfx + delta, 2)))
        self.gestor.datos["ajustes"]["volumen_sfx"] = self.vol_sfx
        self.gestor.guardar()
        self.aplicar_volumenes()

    def alternar_silencio(self):
        self.silenciado = not self.silenciado
        self.gestor.datos["ajustes"]["silencio"] = self.silenciado
        self.gestor.guardar()
        self.aplicar_volumenes()

    # --- SINTETIZADOR PROCEDURAL DE AUDIO DE ALTA CALIDAD ---

    def _sintetizar_onda(self, freq, duracion, tipo="piano"):
        sample_rate = 44100
        n_samples = int(sample_rate * duracion)
        t = np.linspace(0, duracion, n_samples, False)

        if tipo == "piano":
            # Modelo físico simplificado: fundamental + armónicos ricos
            onda = (
                0.55 * np.sin(2 * np.pi * freq * t)
                + 0.28 * np.sin(2 * np.pi * (2 * freq) * t) * np.exp(-1.5 * t)
                + 0.14 * np.sin(2 * np.pi * (3 * freq) * t) * np.exp(-3.0 * t)
                + 0.08 * np.sin(2 * np.pi * (4 * freq) * t) * np.exp(-5.0 * t)
            )
            # Envolvente ADSR de piano: ataque instantáneo de martillo y decaimiento natural
            ataque = np.minimum(t / 0.005, 1.0)
            decaimiento = np.exp(-4.5 * t)
            envolvente = ataque * decaimiento
            onda = onda * envolvente

        elif tipo == "chime":
            # Sonido de campana celestial cristalina (para PERFECT)
            onda = (
                0.5 * np.sin(2 * np.pi * freq * t)
                + 0.3 * np.sin(2 * np.pi * (2.76 * freq) * t)
                + 0.2 * np.sin(2 * np.pi * (5.4 * freq) * t)
            ) * np.exp(-7.0 * t)

        elif tipo == "click":
            # Tacto sutil de UI
            onda = np.sin(2 * np.pi * freq * t) * np.exp(-35.0 * t)

        elif tipo == "thud":
            # Golpe grave seco de fallo
            freq_sweep = freq * np.exp(-12.0 * t)
            onda = 0.8 * np.sin(2 * np.pi * freq_sweep * t) * np.exp(-14.0 * t)

        else:
            onda = np.sin(2 * np.pi * freq * t) * np.exp(-5.0 * t)

        # Normalizar y convertir a estéreo int16
        onda = np.clip(onda, -1.0, 1.0)
        samples = (onda * 32767 * 0.85).astype(np.int16)
        stereo = np.column_stack((samples, samples))
        return pygame.sndarray.make_sound(stereo)

    def _generar_libreria_sfx(self):
        try:
            self.sfx_cache["perfect"] = self._sintetizar_onda(880.0, 0.35, "chime")
            self.sfx_cache["great"] = self._sintetizar_onda(659.25, 0.25, "piano")
            self.sfx_cache["good"] = self._sintetizar_onda(523.25, 0.18, "piano")
            self.sfx_cache["miss"] = self._sintetizar_onda(120.0, 0.3, "thud")
            self.sfx_cache["click"] = self._sintetizar_onda(900.0, 0.06, "click")
            self.sfx_cache["hover"] = self._sintetizar_onda(600.0, 0.04, "click")
            self.sfx_cache["fever"] = self._sintetizar_onda(1046.5, 0.4, "chime")
        except Exception as e:
            print(f"[Sonido] Error creando SFX: {e}")

    def _generar_banco_piano(self):
        """Genera notas de piano para 3 octavas completas (C3 a C6)."""
        nombres = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        # A4 = 440 Hz
        try:
            for octava in range(3, 6):
                for i, nombre in enumerate(nombres):
                    n_semitonos = (octava - 4) * 12 + (i - 9)
                    freq = 440.0 * (2.0 ** (n_semitonos / 12.0))
                    clave = f"{nombre}{octava}"
                    self.notas_piano[clave] = self._sintetizar_onda(freq, 0.65, "piano")
        except Exception as e:
            print(f"[Sonido] Error creando banco de piano: {e}")

    def tocar_nota_carril(self, carril, nota=None):
        if not self.disponible or self.silenciado:
            return
        if nota and nota in self.notas_piano:
            snd = self.notas_piano[nota]
        else:
            # Pentatónica brillante por carril (D=C4, F=E4, J=G4, K=C5)
            escalas_carril = ["C4", "E4", "G4", "C5"]
            clave = escalas_carril[carril % len(escalas_carril)]
            snd = self.notas_piano.get(clave)

        if snd:
            snd.set_volume(self.vol_sfx)
            snd.play()

    def reproducir_sfx(self, nombre):
        if not self.disponible or self.silenciado:
            return
        snd = self.sfx_cache.get(nombre)
        if snd:
            snd.set_volume(self.vol_sfx)
            snd.play()

    # --- REPRODUCTOR DE MÚSICA DE FONDO (CANCIÓN) ---

    def reproducir_archivo(self, ruta_archivo, repetir=True):
        if not self.disponible:
            return False, "Audio no disponible en el sistema"
        try:
            ruta = Path(ruta_archivo)
            if not ruta.exists() or ruta.stat().st_size == 0:
                return False, "El archivo de audio está vacío o no existe"

            # Intentar cargar en pygame mixer music
            pygame.mixer.music.load(str(ruta))
            self.aplicar_volumenes()
            pygame.mixer.music.play(-1 if repetir else 0)
            return True, ""
        except Exception as e:
            return False, f"Formato no compatible: {e}"

    def detener_musica(self):
        if self.disponible:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def pausar_musica(self):
        if self.disponible:
            try:
                pygame.mixer.music.pause()
            except Exception:
                pass

    def reanudar_musica(self):
        if self.disponible:
            try:
                pygame.mixer.music.unpause()
            except Exception:
                pass
