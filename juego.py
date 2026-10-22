import math
import random
import sys
import pygame
from pathlib import Path

import configuracion as cfg
from bloque import Bloque
from canciones_data import CatalogoCanciones
from datos import GestorDatos
from particulas import SistemaEfectos
from sonidos import MotorSonido
from ui import BarraProgreso, BarraVida, Boton, dibujar_panel_cristal, dibujar_rango_insignia


class Juego:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.pantalla = pygame.display.set_mode((cfg.ANCHO, cfg.ALTO))
        pygame.display.set_caption(cfg.TITULO)

        self.reloj = pygame.time.Clock()
        self.abierto = True

        # Tipografías limpias y legibles
        self.fuente_micro = pygame.font.SysFont("segoeui,arial", 13)
        self.fuente_peq = pygame.font.SysFont("segoeui,arial", 16)
        self.fuente_med = pygame.font.SysFont("segoeui,arial", 21, bold=True)
        self.fuente_gra = pygame.font.SysFont("segoeui,arial", 32, bold=True)
        self.fuente_tit = pygame.font.SysFont("segoeui,arial", 46, bold=True)

        # Módulos del juego
        self.datos = GestorDatos()
        self.sonidos = MotorSonido(self.datos)
        self.efectos = SistemaEfectos()
        self.catalogo = CatalogoCanciones()

        # Componentes UI de gameplay
        self.barra_vida = BarraVida(16, 20, 150, 16)
        self.barra_progreso = BarraProgreso(16, 120, cfg.ANCHO - 32, 6)

        # Estado del juego: 'menu', 'seleccion', 'jugando', 'pausa', 'resultados', 'ajustes'
        self.estado = "menu"

        # Variables de partida
        self.cancion_actual = None
        self.indice_cancion = 0
        self.es_modo_arcade = False

        self.bloques = []
        self.notas_pendientes = []
        self.tiempo_juego = 0.0

        # Métricas de la partida
        self.puntos = 0
        self.puntos_animados = 0
        self.hp = cfg.HP_INICIAL
        self.combo = 0
        self.max_combo = 0
        self.conteo_perfect = 0
        self.conteo_great = 0
        self.conteo_good = 0
        self.conteo_miss = 0

        # Iluminación de carriles al presionar
        self.carril_presionado = [False] * cfg.CARRILES
        self.carril_luz_tiempo = [0.0] * cfg.CARRILES

        # Teclas configurables
        self.teclas = list(cfg.TECLAS_DEFAULT)

        # Inicializar botones de navegación
        self._inicializar_botones()

    def _inicializar_botones(self):
        # Botones Menú Principal
        cx = cfg.ANCHO // 2
        w, h = 280, 52
        self.btn_jugar = Boton((cx - w // 2, 430, w, h), "SELECCIONAR CANCIÓN", self.fuente_med, atajo="ENTER")
        self.btn_arcade = Boton((cx - w // 2, 498, w, h), "MODO ARCADE INFINITO", self.fuente_med, atajo="ESPACIO")
        self.btn_ajustes = Boton((cx - w // 2, 566, w, h), "AJUSTES / VOLUMEN", self.fuente_med, atajo="O")
        self.btn_salir = Boton((cx - w // 2, 634, w, h), "SALIR DEL JUEGO", self.fuente_med, atajo="ESC")

        # Botones Selección Canción
        self.btn_sel_ant = Boton((30, 680, 100, 48), "< PREV", self.fuente_med, atajo="IZQ")
        self.btn_sel_jugar = Boton((145, 680, 230, 48), "JUGAR AHORA", self.fuente_med, color_base=(0, 150, 180), atajo="ENTER")
        self.btn_sel_sig = Boton((390, 680, 100, 48), "SIG >", self.fuente_med, atajo="DER")
        self.btn_sel_volver = Boton((30, 746, cfg.ANCHO - 60, 42), "VOLVER AL MENÚ", self.fuente_peq, atajo="ESC")

        # Botones Pausa
        self.btn_pausa_reanudar = Boton((cx - 130, 360, 260, 48), "REANUDAR", self.fuente_med, atajo="ESC")
        self.btn_pausa_reiniciar = Boton((cx - 130, 425, 260, 48), "REINICIAR CANCIÓN", self.fuente_med, atajo="R")
        self.btn_pausa_menu = Boton((cx - 130, 490, 260, 48), "SALIR AL MENÚ", self.fuente_med, atajo="Q")

        # Botones Resultados
        self.btn_res_reintentar = Boton((50, 690, 200, 50), "REINTENTAR", self.fuente_med, atajo="R")
        self.btn_res_menu = Boton((270, 690, 200, 50), "CONTINUAR", self.fuente_med, atajo="ENTER")

        # Botones Ajustes
        self.btn_ajustes_volver = Boton((cx - 130, 680, 260, 48), "GUARDAR Y VOLVER", self.fuente_med, atajo="ESC")

    # --- INICIO Y CONTROL DE PARTIDA ---

    def iniciar_partida(self, cancion=None, modo_arcade=False):
        self.es_modo_arcade = modo_arcade
        self.cancion_actual = cancion or self.catalogo.canciones[self.indice_cancion]

        self.bloques.clear()
        self.tiempo_juego = 0.0
        self.puntos = 0
        self.puntos_animados = 0
        self.hp = cfg.HP_INICIAL
        self.combo = 0
        self.max_combo = 0
        self.conteo_perfect = 0
        self.conteo_great = 0
        self.conteo_good = 0
        self.conteo_miss = 0

        self.carril_presionado = [False] * cfg.CARRILES
        self.carril_luz_tiempo = [0.0] * cfg.CARRILES

        if self.es_modo_arcade:
            self.notas_pendientes = []
            self.tiempo_proximo_bloque_arcade = 0.8
        else:
            # Copiar lista de notas ordenadas cronológicamente
            self.notas_pendientes = sorted(self.cancion_actual.notas, key=lambda n: n[0])

            # Iniciar audio de acompañamiento si existe
            if self.cancion_actual.ruta_audio:
                self.sonidos.reproducir_archivo(self.cancion_actual.ruta_audio, repetir=False)

        self.estado = "jugando"

    def terminar_partida(self, victoria=True):
        self.sonidos.detener_musica()
        if victoria:
            self.sonidos.reproducir_sfx("fever")
        else:
            self.sonidos.reproducir_sfx("miss")

        # Cálculo de estadísticas finales
        total_notas = self.conteo_perfect + self.conteo_great + self.conteo_good + self.conteo_miss
        if total_notas > 0:
            aciertos_ponderados = (self.conteo_perfect * 1.0) + (self.conteo_great * 0.7) + (self.conteo_good * 0.4)
            precision = (aciertos_ponderados / total_notas) * 100.0
        else:
            precision = 0.0

        # Rango
        if not victoria or precision < 55.0:
            rango = "F"
        elif precision >= 98.0 and self.conteo_miss == 0:
            rango = "S+"
        elif precision >= 94.0:
            rango = "S"
        elif precision >= 85.0:
            rango = "A"
        elif precision >= 70.0:
            rango = "B"
        else:
            rango = "C"

        estrellas = 3 if rango in ("S+", "S") else (2 if rango == "A" else (1 if rango in ("B", "C") else 0))

        # Guardar récord
        id_cancion = "arcade" if self.es_modo_arcade else self.cancion_actual.id
        self.es_nuevo_record = self.datos.actualizar_record(
            id_cancion, self.puntos, self.max_combo, rango, estrellas
        )
        self.datos.registrar_partida(self.conteo_perfect, total_notas)

        self.resultado_victoria = victoria
        self.resultado_precision = round(precision, 1)
        self.resultado_rango = rango
        self.estado = "resultados"

    # --- INPUT Y HIT DETECTION ---

    def procesar_presion_carril(self, carril):
        if self.estado != "jugando":
            return

        self.carril_presionado[carril] = True
        self.carril_luz_tiempo[carril] = 0.18

        # Buscar bloques en este carril
        candidatos = [b for b in self.bloques if b.carril == carril and b.estado == "activa"]

        if not candidatos:
            # Pulsó al vacío fuera de tiempo
            self.registrar_fallo("¡FUERA DE TIEMPO!", carril)
            return

        # Seleccionar el más cercano a la línea
        bloque = min(candidatos, key=lambda b: abs(b.centro_cabeza_y - cfg.LINEA_IMPACTO))
        juicio, dist = bloque.evaluar_impacto()

        if juicio is None:
            # Pulsó demasiado pronto
            self.registrar_fallo("¡DEMASIADO PRONTO!", carril)
            return

        # Registrar acierto
        self.registrar_acierto(bloque, juicio, carril)

    def procesar_liberacion_carril(self, carril):
        self.carril_presionado[carril] = False
        for b in self.bloques:
            if b.carril == carril and b.estado == "manteniendo":
                # Si se libera antes de la cola, verificar si completó suficiente
                if (b.y + b.alto / 2) < (cfg.LINEA_IMPACTO - cfg.ZONA_GOOD):
                    b.estado = "fallada"
                else:
                    b.estado = "acertada"

    def registrar_acierto(self, bloque, juicio, carril):
        cx = carril * cfg.ANCHO_CARRIL + cfg.ANCHO_CARRIL // 2
        cy = cfg.LINEA_IMPACTO

        # Sonido de nota de piano
        self.sonidos.tocar_nota_carril(carril, bloque.nota)

        # Multiplicador de combo
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        mult = 1.0 + min(2.0, (self.combo // 15) * 0.25)

        if juicio == "PERFECT":
            self.conteo_perfect += 1
            pts = int(cfg.PUNTOS_PERFECT * mult)
            self.hp = min(cfg.HP_MAXIMO, self.hp + cfg.HP_PERFECT)
            self.efectos.agregar_explosion(cx, cy, cfg.NEON_DORADO, 20)
            self.efectos.agregar_texto("PERFECT!", cx, cy - 25, cfg.NEON_DORADO, self.fuente_med)
            self.sonidos.reproducir_sfx("perfect")

        elif juicio == "GREAT":
            self.conteo_great += 1
            pts = int(cfg.PUNTOS_GREAT * mult)
            self.hp = min(cfg.HP_MAXIMO, self.hp + cfg.HP_GREAT)
            self.efectos.agregar_explosion(cx, cy, cfg.NEON_CYAN, 14)
            self.efectos.agregar_texto("GREAT", cx, cy - 25, cfg.NEON_CYAN, self.fuente_med)
            self.sonidos.reproducir_sfx("great")

        else:  # GOOD
            self.conteo_good += 1
            pts = int(cfg.PUNTOS_GOOD * mult)
            self.hp = min(cfg.HP_MAXIMO, self.hp + cfg.HP_GOOD)
            self.efectos.agregar_explosion(cx, cy, cfg.NEON_VERDE, 8)
            self.efectos.agregar_texto("GOOD", cx, cy - 25, cfg.NEON_VERDE, self.fuente_peq)
            self.sonidos.reproducir_sfx("good")

        self.puntos += pts

        if bloque.es_sostenida:
            bloque.estado = "manteniendo"
        else:
            bloque.estado = "acertada"
            if bloque in self.bloques:
                self.bloques.remove(bloque)

    def registrar_fallo(self, mensaje, carril=None):
        self.combo = 0
        self.conteo_miss += 1
        self.hp = max(0.0, self.hp + cfg.HP_FALLO)
        self.sonidos.reproducir_sfx("miss")
        self.efectos.trigger_shake(6.0, 0.2)

        if carril is not None:
            cx = carril * cfg.ANCHO_CARRIL + cfg.ANCHO_CARRIL // 2
            self.efectos.agregar_explosion(cx, cfg.LINEA_IMPACTO, cfg.NEON_ROJO, 12)
            self.efectos.agregar_texto("MISS", cx, cfg.LINEA_IMPACTO - 25, cfg.NEON_ROJO, self.fuente_med)

        if self.hp <= 0:
            self.terminar_partida(victoria=False)

    # --- BUCLE DE ACTUALIZACIÓN ---

    def actualizar(self, dt):
        pos_mouse = pygame.mouse.get_pos()
        self.efectos.actualizar(dt)

        # Transición suave de puntuación
        if self.puntos_animados < self.puntos:
            self.puntos_animados = min(self.puntos, self.puntos_animados + int(max(1, (self.puntos - self.puntos_animados) * dt * 12)))

        if self.estado == "menu":
            self.btn_jugar.actualizar(pos_mouse, dt)
            self.btn_arcade.actualizar(pos_mouse, dt)
            self.btn_ajustes.actualizar(pos_mouse, dt)
            self.btn_salir.actualizar(pos_mouse, dt)

        elif self.estado == "seleccion":
            self.btn_sel_ant.actualizar(pos_mouse, dt)
            self.btn_sel_jugar.actualizar(pos_mouse, dt)
            self.btn_sel_sig.actualizar(pos_mouse, dt)
            self.btn_sel_volver.actualizar(pos_mouse, dt)

        elif self.estado == "pausa":
            self.btn_pausa_reanudar.actualizar(pos_mouse, dt)
            self.btn_pausa_reiniciar.actualizar(pos_mouse, dt)
            self.btn_pausa_menu.actualizar(pos_mouse, dt)

        elif self.estado == "resultados":
            self.btn_res_reintentar.actualizar(pos_mouse, dt)
            self.btn_res_menu.actualizar(pos_mouse, dt)

        elif self.estado == "ajustes":
            self.btn_ajustes_volver.actualizar(pos_mouse, dt)

        elif self.estado == "jugando":
            self.tiempo_juego += dt
            self.barra_vida.actualizar(self.hp, dt)

            # Enfriamiento de luces de carriles
            for c in range(cfg.CARRILES):
                if self.carril_luz_tiempo[c] > 0:
                    self.carril_luz_tiempo[c] = max(0.0, self.carril_luz_tiempo[c] - dt)

            # Spawn de notas
            velocidad = cfg.VELOCIDAD_DEFAULT + min(300, (self.combo // 20) * 20)

            if self.es_modo_arcade:
                self.tiempo_proximo_bloque_arcade -= dt
                if self.tiempo_proximo_bloque_arcade <= 0:
                    carril = random.randrange(cfg.CARRILES)
                    sost = random.random() < 0.18
                    self.bloques.append(Bloque(carril, es_sostenida=sost, longitud=150 if sost else 0))
                    # Rampa de aceleración en modo arcade
                    dificultad_factor = max(0.28, 0.65 - (self.tiempo_juego * 0.003))
                    self.tiempo_proximo_bloque_arcade = dificultad_factor
            else:
                # Tiempo anticipado de spawn para que la nota llegue a la línea en su timestamp exacto
                tiempo_caida = (cfg.LINEA_IMPACTO - cfg.INICIO_PISTA) / velocidad
                tiempo_spawn = self.tiempo_juego + tiempo_caida

                while self.notas_pendientes and self.notas_pendientes[0][0] <= tiempo_spawn:
                    t_nota, c, nota_p, es_sost, lon = self.notas_pendientes.pop(0)
                    self.bloques.append(Bloque(c, nota=nota_p, es_sostenida=es_sost, longitud=lon))

            # Actualizar bloques en pantalla
            for b in list(self.bloques):
                b.actualizar(dt, velocidad)

                # Bloques sostenidos mientras se mantienen
                if b.estado == "manteniendo":
                    self.puntos += int(200 * dt)
                    self.hp = min(cfg.HP_MAXIMO, self.hp + 1.5 * dt)
                    cx = b.carril * cfg.ANCHO_CARRIL + cfg.ANCHO_CARRIL // 2
                    if random.random() < 0.3:
                        self.efectos.agregar_explosion(cx, cfg.LINEA_IMPACTO, cfg.NEON_MAGENTA, 2)

                # Comprobar si se pasó
                if b.se_paso():
                    if b in self.bloques:
                        self.bloques.remove(b)
                    self.registrar_fallo("MISS", b.carril)

            # Verificar fin de canción en modo estándar
            if not self.es_modo_arcade:
                if not self.notas_pendientes and len(self.bloques) == 0:
                    self.terminar_partida(victoria=True)

    # --- PROCESAMIENTO DE EVENTOS ---

    def procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.abierto = False
                return

            # Controles de mouse / toque táctil en carriles
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = evento.pos
                if self.estado == "jugando" and my >= cfg.INICIO_PISTA:
                    carril = min(cfg.CARRILES - 1, max(0, mx // cfg.ANCHO_CARRIL))
                    self.procesar_presion_carril(carril)

            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                if self.estado == "jugando":
                    for c in range(cfg.CARRILES):
                        if self.carril_presionado[c]:
                            self.procesar_liberacion_carril(c)

            # Interacción con botones de UI según estado
            if self.estado == "menu":
                if self.btn_jugar.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.estado = "seleccion"
                elif self.btn_arcade.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.iniciar_partida(modo_arcade=True)
                elif self.btn_ajustes.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.estado = "ajustes"
                elif self.btn_salir.es_clickeado(evento):
                    self.abierto = False

            elif self.estado == "seleccion":
                if self.btn_sel_ant.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.indice_cancion = (self.indice_cancion - 1) % len(self.catalogo.canciones)
                elif self.btn_sel_sig.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.indice_cancion = (self.indice_cancion + 1) % len(self.catalogo.canciones)
                elif self.btn_sel_jugar.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.iniciar_partida(self.catalogo.canciones[self.indice_cancion])
                elif self.btn_sel_volver.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.estado = "menu"

            elif self.estado == "pausa":
                if self.btn_pausa_reanudar.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.sonidos.reanudar_musica()
                    self.estado = "jugando"
                elif self.btn_pausa_reiniciar.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.iniciar_partida(self.cancion_actual, self.es_modo_arcade)
                elif self.btn_pausa_menu.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.sonidos.detener_musica()
                    self.estado = "menu"

            elif self.estado == "resultados":
                if self.btn_res_reintentar.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.iniciar_partida(self.cancion_actual, self.es_modo_arcade)
                elif self.btn_res_menu.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.estado = "seleccion"

            elif self.estado == "ajustes":
                if self.btn_ajustes_volver.es_clickeado(evento):
                    self.sonidos.reproducir_sfx("click")
                    self.estado = "menu"

            # Eventos de teclado
            if evento.type == pygame.KEYDOWN:
                tecla = evento.key

                # Control global de audio
                if tecla == pygame.K_m:
                    self.sonidos.alternar_silencio()
                elif tecla == pygame.K_UP:
                    self.sonidos.cambiar_volumen_musica(0.05)
                elif tecla == pygame.K_DOWN:
                    self.sonidos.cambiar_volumen_musica(-0.05)

                if self.estado == "menu":
                    if tecla == pygame.K_RETURN:
                        self.estado = "seleccion"
                    elif tecla == pygame.K_SPACE:
                        self.iniciar_partida(modo_arcade=True)
                    elif tecla == pygame.K_o:
                        self.estado = "ajustes"
                    elif tecla == pygame.K_ESCAPE:
                        self.abierto = False

                elif self.estado == "seleccion":
                    if tecla == pygame.K_LEFT:
                        self.indice_cancion = (self.indice_cancion - 1) % len(self.catalogo.canciones)
                    elif tecla == pygame.K_RIGHT:
                        self.indice_cancion = (self.indice_cancion + 1) % len(self.catalogo.canciones)
                    elif tecla == pygame.K_RETURN:
                        self.iniciar_partida(self.catalogo.canciones[self.indice_cancion])
                    elif tecla == pygame.K_ESCAPE:
                        self.estado = "menu"

                elif self.estado == "jugando":
                    if tecla == pygame.K_ESCAPE or tecla == pygame.K_p:
                        self.sonidos.pausar_musica()
                        self.estado = "pausa"
                    elif tecla in self.teclas:
                        carril = self.teclas.index(tecla)
                        self.procesar_presion_carril(carril)

                elif self.estado == "pausa":
                    if tecla == pygame.K_ESCAPE or tecla == pygame.K_RETURN:
                        self.sonidos.reanudar_musica()
                        self.estado = "jugando"
                    elif tecla == pygame.K_r:
                        self.iniciar_partida(self.cancion_actual, self.es_modo_arcade)
                    elif tecla == pygame.K_q:
                        self.sonidos.detener_musica()
                        self.estado = "menu"

                elif self.estado == "resultados":
                    if tecla == pygame.K_r:
                        self.iniciar_partida(self.cancion_actual, self.es_modo_arcade)
                    elif tecla in (pygame.K_RETURN, pygame.K_ESCAPE):
                        self.estado = "seleccion"

                elif self.estado == "ajustes":
                    if tecla in (pygame.K_ESCAPE, pygame.K_RETURN):
                        self.estado = "menu"

            elif evento.type == pygame.KEYUP:
                if self.estado == "jugando" and evento.key in self.teclas:
                    carril = self.teclas.index(evento.key)
                    self.procesar_liberacion_carril(carril)

    # --- RENDERIZADO VISUAL ---

    def dibujar(self):
        # Aplicar sacudida de pantalla si está activa
        ox, oy = self.efectos.obtener_offset_shake()
        superficie_render = self.pantalla

        superficie_render.fill(cfg.FONDO)

        if self.estado == "menu":
            self.dibujar_menu(superficie_render)
        elif self.estado == "seleccion":
            self.dibujar_seleccion(superficie_render)
        elif self.estado == "jugando":
            self.dibujar_pista(superficie_render)
            self.dibujar_hud(superficie_render)
        elif self.estado == "pausa":
            self.dibujar_pista(superficie_render)
            self.dibujar_hud(superficie_render)
            self.dibujar_pausa(superficie_render)
        elif self.estado == "resultados":
            self.dibujar_resultados(superficie_render)
        elif self.estado == "ajustes":
            self.dibujar_ajustes(superficie_render)

        # Capa superior de efectos y partículas
        self.efectos.dibujar(superficie_render)

        # Si hubo shake, desplazar en el flip
        if ox != 0 or oy != 0:
            self.pantalla.blit(superficie_render, (ox, oy))

        pygame.display.flip()

    def dibujar_pista(self, pantalla):
        # Fondo de pista
        rect_pista = pygame.Rect(0, cfg.INICIO_PISTA, cfg.ANCHO, cfg.ALTO - cfg.INICIO_PISTA)
        pygame.draw.rect(pantalla, cfg.FONDO_PISTA, rect_pista)

        # Carriles
        for c in range(cfg.CARRILES):
            x = c * cfg.ANCHO_CARRIL
            color_carril = cfg.CARRIL_A if c % 2 == 0 else cfg.CARRIL_B

            # Efecto de destello en carril activo
            if self.carril_luz_tiempo[c] > 0 or self.carril_presionado[c]:
                color_carril = (35, 45, 75)

            pygame.draw.rect(pantalla, color_carril, (x, cfg.INICIO_PISTA, cfg.ANCHO_CARRIL, rect_pista.height))
            pygame.draw.line(pantalla, cfg.LINEA_DIVISORIA, (x, cfg.INICIO_PISTA), (x, cfg.ALTO), 1)

        # Dibujar casillas que caen
        for b in self.bloques:
            b.dibujar(pantalla)

        # Zona de impacto brillante
        y_zona = cfg.LINEA_IMPACTO - cfg.ZONA_GOOD
        h_zona = cfg.ZONA_GOOD * 2
        zona_surf = pygame.Surface((cfg.ANCHO, h_zona), pygame.SRCALPHA)
        zona_surf.fill((*cfg.NEON_CYAN, 18))
        pantalla.blit(zona_surf, (0, y_zona))

        # Línea de impacto de neón
        pygame.draw.line(pantalla, cfg.NEON_CYAN, (0, cfg.LINEA_IMPACTO), (cfg.ANCHO, cfg.LINEA_IMPACTO), 3)

        # Panel inferior de botones / teclas
        panel_inferior = pygame.Rect(0, cfg.ALTO - 75, cfg.ANCHO, 75)
        pygame.draw.rect(pantalla, cfg.FONDO_PANEL, panel_inferior)
        pygame.draw.line(pantalla, cfg.LINEA_DIVISORIA, (0, panel_inferior.top), (cfg.ANCHO, panel_inferior.top), 2)

        for c, eti in enumerate(cfg.ETIQUETAS_TECLAS):
            cx = c * cfg.ANCHO_CARRIL + cfg.ANCHO_CARRIL // 2
            cy = panel_inferior.centery

            activo = self.carril_presionado[c] or self.carril_luz_tiempo[c] > 0
            color_btn = cfg.NEON_CYAN if activo else cfg.GRIS_MEDIO

            # Círculo tecla
            pygame.draw.circle(pantalla, (20, 26, 42) if not activo else (40, 60, 90), (cx, cy), 22)
            pygame.draw.circle(pantalla, color_btn, (cx, cy), 22, width=2)

            img_letra = self.fuente_med.render(eti, True, cfg.BLANCO if activo else cfg.GRIS_CLARO)
            pantalla.blit(img_letra, img_letra.get_rect(center=(cx, cy)))

        # Borde FEVER si el combo es alto
        if self.combo >= 25:
            borde_glow = pygame.Surface((cfg.ANCHO, cfg.ALTO), pygame.SRCALPHA)
            pygame.draw.rect(borde_glow, (*cfg.NEON_MAGENTA, 40), (0, 0, cfg.ANCHO, cfg.ALTO), width=6)
            pantalla.blit(borde_glow, (0, 0))

    def dibujar_hud(self, pantalla):
        # Barra superior de información
        rect_cabecera = pygame.Rect(0, 0, cfg.ANCHO, cfg.INICIO_PISTA)
        pygame.draw.rect(pantalla, cfg.FONDO_PANEL, rect_cabecera)
        pygame.draw.line(pantalla, cfg.LINEA_DIVISORIA, (0, cfg.INICIO_PISTA), (cfg.ANCHO, cfg.INICIO_PISTA), 2)

        # Barra de vida
        lbl_hp = self.fuente_micro.render("VIDA", True, cfg.GRIS_CLARO)
        pantalla.blit(lbl_hp, (16, 4))
        self.barra_vida.dibujar(pantalla)

        # Puntuación animada central
        img_score = self.fuente_gra.render(f"{self.puntos_animados:,}", True, cfg.BLANCO)
        pantalla.blit(img_score, img_score.get_rect(center=(cfg.ANCHO // 2, 45)))

        # Título de canción y artista a la derecha
        titulo_txt = "MODO ARCADE" if self.es_modo_arcade else self.cancion_actual.titulo
        img_tit = self.fuente_peq.render(titulo_txt[:24], True, cfg.NEON_CYAN)
        pantalla.blit(img_tit, (cfg.ANCHO - img_tit.get_width() - 16, 16))

        bpm_txt = f"{self.cancion_actual.bpm if not self.es_modo_arcade else 140} BPM"
        img_bpm = self.fuente_micro.render(bpm_txt, True, cfg.GRIS_CLARO)
        pantalla.blit(img_bpm, (cfg.ANCHO - img_bpm.get_width() - 16, 40))

        # Barra de progreso de la canción
        if not self.es_modo_arcade and self.cancion_actual:
            progreso = min(1.0, self.tiempo_juego / max(1.0, self.cancion_actual.duracion_total))
            self.barra_progreso.dibujar(pantalla, progreso)

        # Indicador de Combo central
        if self.combo >= 3:
            img_combo = self.fuente_gra.render(f"{self.combo}x", True, cfg.NEON_DORADO if self.combo >= 20 else cfg.BLANCO)
            lbl_combo = self.fuente_micro.render("COMBO", True, cfg.GRIS_CLARO)
            pantalla.blit(img_combo, img_combo.get_rect(center=(cfg.ANCHO // 2, 210)))
            pantalla.blit(lbl_combo, lbl_combo.get_rect(center=(cfg.ANCHO // 2, 235)))

    def dibujar_menu(self, pantalla):
        cx = cfg.ANCHO // 2

        # Título Neón
        img_sub = self.fuente_peq.render("PRO AUDIO RHYTHM EXPERIENCE", True, cfg.NEON_CYAN)
        pantalla.blit(img_sub, img_sub.get_rect(center=(cx, 160)))

        img_tit1 = self.fuente_tit.render("CASILLAS", True, cfg.BLANCO)
        img_tit2 = self.fuente_tit.render("RÍTMICAS", True, cfg.NEON_CYAN)
        pantalla.blit(img_tit1, img_tit1.get_rect(center=(cx, 220)))
        pantalla.blit(img_tit2, img_tit2.get_rect(center=(cx, 275)))

        img_sub2 = self.fuente_peq.render("Piano Tiles Edition", True, cfg.NEON_MAGENTA)
        pantalla.blit(img_sub2, img_sub2.get_rect(center=(cx, 335)))

        # Panel de botones
        self.btn_jugar.dibujar(pantalla)
        self.btn_arcade.dibujar(pantalla)
        self.btn_ajustes.dibujar(pantalla)
        self.btn_salir.dibujar(pantalla)

        # Estadísticas del jugador
        stats = self.datos.datos["estadisticas"]
        info_txt = f"Partidas jugadas: {stats['partidas_jugadas']}  |  Notas Perfectas: {stats['notas_perfectas']}"
        img_stats = self.fuente_micro.render(info_txt, True, cfg.GRIS_MEDIO)
        pantalla.blit(img_stats, img_stats.get_rect(center=(cx, 790)))

    def dibujar_seleccion(self, pantalla):
        cx = cfg.ANCHO // 2

        # Cabecera
        img_cab = self.fuente_gra.render("SELECCIONA UNA CANCIÓN", True, cfg.BLANCO)
        pantalla.blit(img_cab, img_cab.get_rect(center=(cx, 70)))

        # Tarjeta de canción principal
        c = self.catalogo.canciones[self.indice_cancion]
        rect_card = pygame.Rect(40, 130, cfg.ANCHO - 80, 480)
        dibujar_panel_cristal(pantalla, rect_card, cfg.NEON_CYAN if self.indice_cancion == 0 else cfg.LINEA_DIVISORIA)

        # Ilustración / Disco musical en tarjeta
        cy_disco = rect_card.y + 110
        pygame.draw.circle(pantalla, (25, 32, 52), (cx, cy_disco), 70)
        pygame.draw.circle(pantalla, cfg.NEON_CYAN, (cx, cy_disco), 70, width=2)
        pygame.draw.circle(pantalla, cfg.FONDO, (cx, cy_disco), 24)

        # Título y artista
        img_tit = self.fuente_gra.render(c.titulo, True, cfg.BLANCO)
        pantalla.blit(img_tit, img_tit.get_rect(center=(cx, rect_card.y + 225)))

        img_art = self.fuente_med.render(c.artista, True, cfg.GRIS_CLARO)
        pantalla.blit(img_art, img_art.get_rect(center=(cx, rect_card.y + 265)))

        # Insignias: BPM, Dificultad, Estrellas
        estrellas_str = "★" * c.estrellas + "☆" * (5 - c.estrellas)
        img_est = self.fuente_med.render(estrellas_str, True, cfg.NEON_DORADO)
        pantalla.blit(img_est, img_est.get_rect(center=(cx, rect_card.y + 310)))

        dif_txt = f"{c.dificultad.upper()}  •  {c.bpm} BPM  •  {c.duracion_total}s"
        img_dif = self.fuente_peq.render(dif_txt, True, cfg.NEON_CYAN)
        pantalla.blit(img_dif, img_dif.get_rect(center=(cx, rect_card.y + 345)))

        # Récord personal
        rec = self.datos.obtener_record(c.id)
        rect_rec = pygame.Rect(rect_card.x + 30, rect_card.y + 380, rect_card.width - 60, 65)
        pygame.draw.rect(pantalla, (12, 16, 26), rect_rec, border_radius=8)

        lbl_rec = self.fuente_micro.render("MEJOR PUNTUACIÓN", True, cfg.GRIS_MEDIO)
        pantalla.blit(lbl_rec, (rect_rec.x + 14, rect_rec.y + 12))

        val_rec = self.fuente_med.render(f"{rec['puntos']:,} pts  (Combo: {rec['combo']}x)", True, cfg.BLANCO)
        pantalla.blit(val_rec, (rect_rec.x + 14, rect_rec.y + 32))

        dibujar_rango_insignia(pantalla, rec.get("rango", "-"), rect_rec.right - 35, rect_rec.centery, self.fuente_med)

        # Controles inferiores
        self.btn_sel_ant.dibujar(pantalla)
        self.btn_sel_jugar.dibujar(pantalla)
        self.btn_sel_sig.dibujar(pantalla)
        self.btn_sel_volver.dibujar(pantalla)

    def dibujar_pausa(self, pantalla):
        # Capa translúcida oscura
        overlay = pygame.Surface((cfg.ANCHO, cfg.ALTO), pygame.SRCALPHA)
        overlay.fill((5, 8, 14, 210))
        pantalla.blit(overlay, (0, 0))

        cx = cfg.ANCHO // 2
        img_p = self.fuente_tit.render("PAUSA", True, cfg.NEON_CYAN)
        pantalla.blit(img_p, img_p.get_rect(center=(cx, 260)))

        self.btn_pausa_reanudar.dibujar(pantalla)
        self.btn_pausa_reiniciar.dibujar(pantalla)
        self.btn_pausa_menu.dibujar(pantalla)

    def dibujar_resultados(self, pantalla):
        cx = cfg.ANCHO // 2

        # Panel de resultados
        rect_res = pygame.Rect(35, 60, cfg.ANCHO - 70, 600)
        dibujar_panel_cristal(pantalla, rect_res, cfg.NEON_DORADO if self.resultado_victoria else cfg.NEON_ROJO)

        titulo_res = "¡CANCIÓN COMPLETADA!" if self.resultado_victoria else "FIN DE LA PARTIDA"
        color_res = cfg.NEON_VERDE if self.resultado_victoria else cfg.NEON_ROJO
        img_tit = self.fuente_gra.render(titulo_res, True, color_res)
        pantalla.blit(img_tit, img_tit.get_rect(center=(cx, 115)))

        # Rango grande
        dibujar_rango_insignia(pantalla, self.resultado_rango, cx, 190, self.fuente_tit)

        # Puntuación final
        img_score = self.fuente_tit.render(f"{self.puntos:,}", True, cfg.BLANCO)
        pantalla.blit(img_score, img_score.get_rect(center=(cx, 270)))

        if getattr(self, "es_nuevo_record", False):
            badge = self.fuente_peq.render("★ ¡NUEVO RÉCORD PERSONAL! ★", True, cfg.NEON_DORADO)
            pantalla.blit(badge, badge.get_rect(center=(cx, 315)))

        # Desglose de precisión
        lineas = [
            ("Precisión Global", f"{self.resultado_precision}%", cfg.BLANCO),
            ("Combo Máximo", f"{self.max_combo}x", cfg.NEON_CYAN),
            ("PERFECT", str(self.conteo_perfect), cfg.NEON_DORADO),
            ("GREAT", str(self.conteo_great), cfg.NEON_CYAN),
            ("GOOD", str(self.conteo_good), cfg.NEON_VERDE),
            ("MISS", str(self.conteo_miss), cfg.NEON_ROJO),
        ]

        y_offset = 360
        for etiqueta, valor, col in lineas:
            img_e = self.fuente_peq.render(etiqueta, True, cfg.GRIS_CLARO)
            img_v = self.fuente_med.render(valor, True, col)
            pantalla.blit(img_e, (rect_res.x + 35, y_offset))
            pantalla.blit(img_v, (rect_res.right - 35 - img_v.get_width(), y_offset - 2))
            y_offset += 38

        # Botones de acción
        self.btn_res_reintentar.dibujar(pantalla)
        self.btn_res_menu.dibujar(pantalla)

    def dibujar_ajustes(self, pantalla):
        cx = cfg.ANCHO // 2

        img_tit = self.fuente_gra.render("AJUSTES DE AUDIO", True, cfg.BLANCO)
        pantalla.blit(img_tit, img_tit.get_rect(center=(cx, 120)))

        rect_panel = pygame.Rect(40, 180, cfg.ANCHO - 80, 440)
        dibujar_panel_cristal(pantalla, rect_panel)

        # Volumen Música
        vol_m = int(self.sonidos.vol_musica * 100)
        img_m = self.fuente_med.render(f"Volumen Música: {vol_m}%", True, cfg.BLANCO)
        pantalla.blit(img_m, (rect_panel.x + 30, 230))
        img_hint_m = self.fuente_peq.render("Usa FLECHA ARRIBA / ABAJO", True, cfg.GRIS_CLARO)
        pantalla.blit(img_hint_m, (rect_panel.x + 30, 265))

        # Silencio
        estado_sil = "SILENCIADO" if self.sonidos.silenciado else "ACTIVO"
        col_sil = cfg.NEON_ROJO if self.sonidos.silenciado else cfg.NEON_VERDE
        img_s = self.fuente_med.render(f"Estado de Audio: {estado_sil}", True, col_sil)
        pantalla.blit(img_s, (rect_panel.x + 30, 330))
        img_hint_s = self.fuente_peq.render("Pulsa 'M' para alternar silencio", True, cfg.GRIS_CLARO)
        pantalla.blit(img_hint_s, (rect_panel.x + 30, 365))

        # Teclas de control
        img_t = self.fuente_med.render("Controles de Carril:", True, cfg.BLANCO)
        pantalla.blit(img_t, (rect_panel.x + 30, 430))
        etiquetas_str = "    ".join(cfg.ETIQUETAS_TECLAS)
        img_keys = self.fuente_gra.render(etiquetas_str, True, cfg.NEON_CYAN)
        pantalla.blit(img_keys, (rect_panel.x + 30, 470))

        img_mouse = self.fuente_peq.render("Soporte completo para mouse / táctil", True, cfg.GRIS_CLARO)
        pantalla.blit(img_mouse, (rect_panel.x + 30, 530))

        self.btn_ajustes_volver.dibujar(pantalla)

    def ejecutar(self):
        try:
            while self.abierto:
                dt = min(self.reloj.tick(cfg.FPS) / 1000.0, 0.05)
                self.procesar_eventos()
                self.actualizar(dt)
                self.dibujar()
        finally:
            self.sonidos.detener_musica()
            self.datos.guardar()
            pygame.quit()