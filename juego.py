import random
import pygame

import configuracion as cfg
from bloque import Bloque
from musica import Musica


class Juego:
    def __init__(self):
        pygame.init()

        self.pantalla = pygame.display.set_mode(
            (cfg.ANCHO, cfg.ALTO)
        )
        pygame.display.set_caption(cfg.TITULO)

        self.reloj = pygame.time.Clock()

        self.fuente = pygame.font.SysFont("arial", 23)
        self.pequena = pygame.font.SysFont("arial", 17)
        self.grande = pygame.font.SysFont("arial", 38, bold=True)

        self.musica = Musica()

        self.abierto = True
        self.estado = "menu"
        self.bloques = []
        self.puntos = 0
        self.record = 0
        self.velocidad = cfg.VELOCIDAD_INICIAL
        self.tiempo_generacion = 0
        self.motivo = ""

        # Destello visual por cada acierto
        self.destellos = [0.0] * cfg.CARRILES

    def texto(self, contenido, y, color=None, fuente=None):
        if color is None:
            color = cfg.BLANCO

        if fuente is None:
            fuente = self.fuente

        imagen = fuente.render(contenido, True, color)
        rectangulo = imagen.get_rect(
            center=(cfg.ANCHO // 2, y)
        )
        self.pantalla.blit(imagen, rectangulo)

    def iniciar_partida(self):
        self.bloques.clear()
        self.puntos = 0
        self.velocidad = cfg.VELOCIDAD_INICIAL
        self.tiempo_generacion = 0
        self.destellos = [0.0] * cfg.CARRILES
        self.motivo = ""
        self.estado = "jugando"

        # Primera nota
        self.crear_bloque()
        self.musica.reproducir()

    def crear_bloque(self):
        carril = random.randrange(cfg.CARRILES)
        self.bloques.append(Bloque(carril))

    def terminar_partida(self, motivo):
        self.estado = "derrota"
        self.motivo = motivo
        self.record = max(self.record, self.puntos)
        self.musica.detener()

    def pulsar_carril(self, carril):
        candidatos = [
            bloque
            for bloque in self.bloques
            if bloque.carril == carril
            and bloque.esta_en_zona()
        ]

        if not candidatos:
            self.terminar_partida("Pulsaste fuera de tiempo")
            return

        # Selecciona el bloque más cercano a la línea.
        bloque = min(
            candidatos,
            key=lambda elemento: abs(
                elemento.centro_y - cfg.LINEA_IMPACTO
            ),
        )

        self.bloques.remove(bloque)
        self.puntos += 1
        self.destellos[carril] = 0.15

        nivel = self.puntos // 10

        self.velocidad = min(
            cfg.VELOCIDAD_MAXIMA,
            cfg.VELOCIDAD_INICIAL
            + nivel * cfg.AUMENTO_VELOCIDAD,
        )

    def procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.abierto = False
                continue

            # Si cambias de ventana, vuelve al menú.
            if evento.type == pygame.WINDOWFOCUSLOST:
                if self.estado == "jugando":
                    self.estado = "menu"
                    self.musica.detener()
                continue

            if evento.type != pygame.KEYDOWN:
                continue

            tecla = evento.key

            # Controles disponibles en todas las pantallas
            if tecla == pygame.K_ESCAPE:
                if self.estado == "menu":
                    self.abierto = False
                else:
                    self.estado = "menu"
                    self.musica.detener()
                continue

            if tecla == pygame.K_m:
                self.musica.alternar_silencio()
                continue

            if tecla == pygame.K_UP:
                self.musica.ajustar_volumen(0.1)
                continue

            if tecla == pygame.K_DOWN:
                self.musica.ajustar_volumen(-0.1)
                continue

            # Menú
            if self.estado == "menu":
                if tecla == pygame.K_RETURN:
                    self.iniciar_partida()

                elif tecla == pygame.K_LEFT:
                    self.musica.cambiar(-1)

                elif tecla == pygame.K_RIGHT:
                    self.musica.cambiar(1)

                elif tecla == pygame.K_F5:
                    self.musica.actualizar_lista()

            # Partida
            elif self.estado == "jugando":
                if tecla in cfg.TECLAS:
                    carril = cfg.TECLAS.index(tecla)
                    self.pulsar_carril(carril)

            # Pantalla final
            elif self.estado == "derrota":
                if tecla == pygame.K_r:
                    self.iniciar_partida()

                elif tecla == pygame.K_RETURN:
                    self.estado = "menu"

    def actualizar(self, segundos):
        if self.estado != "jugando":
            return

        for carril in range(cfg.CARRILES):
            self.destellos[carril] = max(
                0,
                self.destellos[carril] - segundos,
            )

        self.tiempo_generacion += segundos

        while self.tiempo_generacion >= cfg.INTERVALO_BLOQUES:
            self.tiempo_generacion -= cfg.INTERVALO_BLOQUES
            self.crear_bloque()

        for bloque in self.bloques:
            bloque.actualizar(segundos, self.velocidad)

            if bloque.se_paso():
                self.terminar_partida("Dejaste pasar un bloque")
                return

    def dibujar_menu(self):
        self.texto(
            "CASILLAS",
            150,
            cfg.ACENTO,
            self.grande,
        )
        self.texto(
            "RÍTMICAS",
            200,
            cfg.BLANCO,
            self.grande,
        )

        self.texto("Cuatro teclas. Un solo ritmo.", 265)
        self.texto("D     F     J     K", 320, cfg.ACENTO)

        self.texto(
            "Pulsa cuando el centro del bloque",
            370,
            fuente=self.pequena,
        )
        self.texto(
            "esté en la franja verde.",
            395,
            fuente=self.pequena,
        )

        self.texto("ENTER: comenzar", 450, cfg.ACENTO)

        nombre = self.musica.nombre_actual()
        if len(nombre) > 34:
            nombre = nombre[:31] + "..."

        self.texto(
            f"Música: {nombre}",
            510,
            fuente=self.pequena,
        )
        self.texto(
            "Izquierda / Derecha: cambiar canción",
            545,
            fuente=self.pequena,
        )
        self.texto(
            "F5: actualizar carpeta canciones",
            575,
            fuente=self.pequena,
        )

        self.dibujar_estado_audio(635)

        self.texto(
            "ESC: salir",
            700,
            cfg.GRIS,
            self.pequena,
        )

    def dibujar_estado_audio(self, y):
        if self.musica.silenciada:
            mensaje = "Música silenciada"
        else:
            porcentaje = round(self.musica.volumen * 100)
            mensaje = f"Volumen: {porcentaje}%"

        self.texto(mensaje, y, cfg.GRIS, self.pequena)

        self.texto(
            "Arriba / Abajo: volumen | M: silenciar",
            y + 25,
            cfg.GRIS,
            self.pequena,
        )

    def dibujar_partida(self):
        pista = pygame.Rect(
            0,
            cfg.INICIO_PISTA,
            cfg.ANCHO,
            cfg.ALTO - cfg.INICIO_PISTA,
        )

        # Recorta el dibujo para no invadir el marcador.
        self.pantalla.set_clip(pista)

        for carril in range(cfg.CARRILES):
            x = carril * cfg.ANCHO_CARRIL

            color = (
                cfg.CARRIL_CLARO
                if carril % 2 == 0
                else cfg.CARRIL_OSCURO
            )

            if self.destellos[carril] > 0:
                color = cfg.ACENTO

            pygame.draw.rect(
                self.pantalla,
                color,
                (
                    x,
                    cfg.INICIO_PISTA,
                    cfg.ANCHO_CARRIL,
                    cfg.ALTO - cfg.INICIO_PISTA,
                ),
            )

            pygame.draw.line(
                self.pantalla,
                cfg.PANEL,
                (x, cfg.INICIO_PISTA),
                (x, cfg.ALTO),
                2,
            )

        for bloque in self.bloques:
            bloque.dibujar(self.pantalla)

        # Franja translúcida de acierto
        zona = pygame.Surface(
            (cfg.ANCHO, cfg.TOLERANCIA * 2),
            pygame.SRCALPHA,
        )
        zona.fill((*cfg.ACENTO, 65))

        self.pantalla.blit(
            zona,
            (0, cfg.LINEA_IMPACTO - cfg.TOLERANCIA),
        )

        pygame.draw.line(
            self.pantalla,
            cfg.ACENTO,
            (0, cfg.LINEA_IMPACTO),
            (cfg.ANCHO, cfg.LINEA_IMPACTO),
            4,
        )

        # Panel inferior de controles
        pygame.draw.rect(
            self.pantalla,
            cfg.PANEL,
            (0, 690, cfg.ANCHO, 70),
        )

        for carril, etiqueta in enumerate(cfg.ETIQUETAS):
            imagen = self.fuente.render(
                etiqueta,
                True,
                cfg.BLANCO,
            )
            rectangulo = imagen.get_rect(
                center=(
                    carril * cfg.ANCHO_CARRIL
                    + cfg.ANCHO_CARRIL // 2,
                    725,
                )
            )
            self.pantalla.blit(imagen, rectangulo)

        self.pantalla.set_clip(None)

        self.texto(
            f"Puntos: {self.puntos}",
            32,
            cfg.ACENTO,
        )
        self.texto(
            f"Nivel: {self.puntos // 10 + 1}",
            65,
        )
        self.texto(
            "ESC: menú | M: silencio | Arriba/Abajo: volumen",
            98,
            cfg.GRIS,
            self.pequena,
        )

    def dibujar_derrota(self):
        self.texto(
            "FIN DE PARTIDA",
            230,
            cfg.ROJO,
            self.grande,
        )

        self.texto(self.motivo, 300)
        self.texto(f"Puntuación: {self.puntos}", 370, cfg.ACENTO)
        self.texto(f"Récord de esta sesión: {self.record}", 415)

        self.texto("R: volver a jugar", 500, cfg.ACENTO)
        self.texto("ENTER: volver al menú", 545)
        self.texto("ESC: volver al menú", 585, cfg.GRIS)

    def dibujar(self):
        self.pantalla.fill(cfg.FONDO)

        if self.estado == "menu":
            self.dibujar_menu()

        elif self.estado == "jugando":
            self.dibujar_partida()

        elif self.estado == "derrota":
            self.dibujar_derrota()

        if self.musica.error:
            self.texto(
                self.musica.error,
                15,
                cfg.ROJO,
                self.pequena,
            )

        pygame.display.flip()

    def ejecutar(self):
        try:
            while self.abierto:
                segundos = min(
                    self.reloj.tick(cfg.FPS) / 1000.0,
                    0.05,
                )

                self.procesar_eventos()

                if not self.abierto:
                    break

                self.actualizar(segundos)
                self.dibujar()

        finally:
            self.musica.detener()
            pygame.quit()