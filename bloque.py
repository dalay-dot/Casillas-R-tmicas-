import pygame
import configuracion as cfg


class Bloque:
    def __init__(self, carril, nota=None, es_sostenida=False, longitud=0):
        self.carril = carril
        self.nota = nota
        self.es_sostenida = es_sostenida
        self.longitud = float(longitud) if es_sostenida else 0.0

        # Posición del borde inferior / cabeza del bloque
        self.y = float(cfg.INICIO_PISTA - cfg.ALTO_BLOQUE - self.longitud)
        self.alto = float(cfg.ALTO_BLOQUE)

        # Estados: 'activa', 'manteniendo', 'acertada', 'fallada'
        self.estado = "activa"
        self.tiempo_mantenido = 0.0
        self.alpha_desvanecer = 255

    @property
    def cabeza_y(self):
        """Borde inferior de la cabeza del bloque."""
        return self.y + self.longitud + self.alto

    @property
    def centro_cabeza_y(self):
        """Centro de la cabeza de impacto."""
        return self.y + self.longitud + (self.alto / 2.0)

    @property
    def cola_y(self):
        """Borde superior de la nota sostenida."""
        return self.y

    def actualizar(self, dt, velocidad):
        self.y += velocidad * dt

        if self.estado == "manteniendo":
            self.tiempo_mantenido += dt

    def evaluar_impacto(self):
        """Evalúa la precisión del impacto y retorna ('PERFECT'/'GREAT'/'GOOD'/None, distancia)."""
        distancia = abs(self.centro_cabeza_y - cfg.LINEA_IMPACTO)
        if distancia <= cfg.ZONA_PERFECT:
            return "PERFECT", distancia
        elif distancia <= cfg.ZONA_GREAT:
            return "GREAT", distancia
        elif distancia <= cfg.ZONA_GOOD:
            return "GOOD", distancia
        return None, distancia

    def se_paso(self):
        """Indica si el bloque ya cruzó la zona de impacto sin ser pulsado."""
        if self.estado == "activa":
            return self.centro_cabeza_y > (cfg.LINEA_IMPACTO + cfg.ZONA_GOOD)
        elif self.estado == "manteniendo":
            # Si se estaba manteniendo, termina cuando la cola cruza la línea
            return (self.y + self.alto / 2) > (cfg.LINEA_IMPACTO + cfg.ZONA_GOOD)
        return False

    def dibujar(self, pantalla):
        if self.estado == "acertada" and self.alpha_desvanecer <= 0:
            return

        x = self.carril * cfg.ANCHO_CARRIL + 8
        ancho = cfg.ANCHO_CARRIL - 16

        # --- DIBUJO DE CUERPO SOSTENIDO (HOLD TRAIL) ---
        if self.es_sostenida and self.longitud > 0:
            rect_cuerpo = pygame.Rect(
                x + 12,
                round(self.y + self.alto / 2),
                ancho - 24,
                round(self.longitud),
            )
            color_cuerpo = (*cfg.NEON_PURPLE, 110)
            superficie_cuerpo = pygame.Surface((rect_cuerpo.width, rect_cuerpo.height), pygame.SRCALPHA)
            superficie_cuerpo.fill(color_cuerpo)
            pygame.draw.rect(
                superficie_cuerpo,
                (*cfg.NEON_CYAN, 180),
                (0, 0, rect_cuerpo.width, rect_cuerpo.height),
                width=2,
                border_radius=6,
            )
            pantalla.blit(superficie_cuerpo, rect_cuerpo.topleft)

        # --- CABEZA DE LA CASILLA (PIANO TILE) ---
        cabeza_top = round(self.y + self.longitud)
        rect_cabeza = pygame.Rect(x, cabeza_top, ancho, round(self.alto))

        # Color base según carril y estado
        color_base = cfg.COLOR_BLOQUE
        color_borde = cfg.COLOR_BLOQUE_BORDE

        if self.estado == "manteniendo":
            color_base = (35, 20, 55)
            color_borde = cfg.NEON_MAGENTA
        elif self.es_sostenida:
            color_borde = cfg.COLOR_BLOQUE_SOSTENIDO

        # Fondo de la casilla
        pygame.draw.rect(
            pantalla,
            color_base,
            rect_cabeza,
            border_radius=12,
        )

        # Borde de neón brillante
        pygame.draw.rect(
            pantalla,
            color_borde,
            rect_cabeza,
            width=3,
            border_radius=12,
        )

        # Brillo superior / Reflejo de cristal (Glassmorphism highlight)
        brillo_rect = pygame.Rect(x + 8, cabeza_top + 8, ancho - 16, 12)
        superficie_brillo = pygame.Surface((brillo_rect.width, brillo_rect.height), pygame.SRCALPHA)
        superficie_brillo.fill((255, 255, 255, 45))
        pantalla.blit(superficie_brillo, brillo_rect.topleft)

        # Acento central estilizado
        centro_x = x + ancho // 2
        centro_y = cabeza_top + round(self.alto) // 2
        pygame.draw.circle(
            pantalla,
            color_borde,
            (centro_x, centro_y),
            6,
        )