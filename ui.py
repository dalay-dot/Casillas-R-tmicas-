import pygame
import configuracion as cfg


class Boton:
    def __init__(self, rect, texto, fuente, color_base=cfg.FONDO_PANEL, color_hover=cfg.NEON_CYAN, color_texto=cfg.BLANCO, atajo=""):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.fuente = fuente
        self.color_base = color_base
        self.color_hover = color_hover
        self.color_texto = color_texto
        self.atajo = atajo
        self.hover = False
        self.anim_progreso = 0.0

    def actualizar(self, pos_mouse, dt):
        self.hover = self.rect.collidepoint(pos_mouse)
        target = 1.0 if self.hover else 0.0
        self.anim_progreso += (target - self.anim_progreso) * min(1.0, dt * 15)

    def es_clickeado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect.collidepoint(evento.pos)
        return False

    def dibujar(self, pantalla):
        # Interpolación de color
        r = int(self.color_base[0] + (self.color_hover[0] - self.color_base[0]) * (self.anim_progreso * 0.25))
        g = int(self.color_base[1] + (self.color_hover[1] - self.color_base[1]) * (self.anim_progreso * 0.25))
        b = int(self.color_base[2] + (self.color_hover[2] - self.color_base[2]) * (self.anim_progreso * 0.25))
        color_fondo = (r, g, b)

        # Fondo del botón
        pygame.draw.rect(pantalla, color_fondo, self.rect, border_radius=10)

        # Borde brillante si está activo
        borde_color = cfg.LINEA_DIVISORIA if self.anim_progreso < 0.1 else self.color_hover
        pygame.draw.rect(pantalla, borde_color, self.rect, width=2, border_radius=10)

        # Si hover, añadir resplandor sutil
        if self.anim_progreso > 0.05:
            resplandor = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            alpha = int(40 * self.anim_progreso)
            resplandor.fill((*self.color_hover, alpha))
            pantalla.blit(resplandor, self.rect.topleft)

        # Texto centrado
        img_texto = self.fuente.render(self.texto, True, self.color_texto)
        rect_texto = img_texto.get_rect(center=self.rect.center)
        pantalla.blit(img_texto, rect_texto)

        # Atajo en la esquina si existe
        if self.atajo:
            fuente_peq = pygame.font.SysFont("arial", 12, bold=True)
            img_atajo = fuente_peq.render(f"[{self.atajo}]", True, cfg.GRIS_CLARO)
            pantalla.blit(img_atajo, (self.rect.right - img_atajo.get_width() - 8, self.rect.top + 6))


class BarraVida:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.hp_actual = cfg.HP_INICIAL
        self.hp_mostrada = cfg.HP_INICIAL
        self.tiempo_alerta = 0.0

    def actualizar(self, hp_real, dt):
        self.hp_actual = max(0.0, min(cfg.HP_MAXIMO, hp_real))
        # Animación suave hacia el valor real
        self.hp_mostrada += (self.hp_actual - self.hp_mostrada) * min(1.0, dt * 10)
        self.tiempo_alerta += dt

    def dibujar(self, pantalla):
        # Contenedor exterior
        pygame.draw.rect(pantalla, cfg.FONDO_PANEL, self.rect, border_radius=6)
        pygame.draw.rect(pantalla, cfg.LINEA_DIVISORIA, self.rect, width=1, border_radius=6)

        porcentaje = self.hp_mostrada / cfg.HP_MAXIMO
        ancho_relleno = max(0, int((self.rect.width - 4) * porcentaje))

        if ancho_relleno > 0:
            # Color dinámico de vida
            if porcentaje > 0.5:
                color_hp = cfg.NEON_VERDE
            elif porcentaje > 0.25:
                color_hp = cfg.NEON_DORADO
            else:
                # Pulso de peligro rojo
                brillo = abs(pygame.math.Vector2(1, 0).rotate(self.tiempo_alerta * 360).x)
                color_hp = (
                    int(200 + 55 * brillo),
                    int(40 * brillo),
                    int(40 * brillo),
                )

            rect_relleno = pygame.Rect(self.rect.x + 2, self.rect.y + 2, ancho_relleno, self.rect.height - 4)
            pygame.draw.rect(pantalla, color_hp, rect_relleno, border_radius=4)


class BarraProgreso:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)

    def dibujar(self, pantalla, porcentaje):
        porcentaje = max(0.0, min(1.0, porcentaje))
        pygame.draw.rect(pantalla, cfg.FONDO_PANEL, self.rect, border_radius=3)
        ancho_val = int(self.rect.width * porcentaje)
        if ancho_val > 0:
            rect_val = pygame.Rect(self.rect.x, self.rect.y, ancho_val, self.rect.height)
            pygame.draw.rect(pantalla, cfg.NEON_CYAN, rect_val, border_radius=3)


def dibujar_panel_cristal(pantalla, rect, color_borde=cfg.LINEA_DIVISORIA, radio=14, alpha=230):
    """Dibuja una tarjeta moderna con efecto glassmorphism oscuro."""
    superficie = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    superficie.fill((*cfg.FONDO_PANEL, alpha))
    pantalla.blit(superficie, rect.topleft)
    pygame.draw.rect(pantalla, color_borde, rect, width=2, border_radius=radio)


def dibujar_rango_insignia(pantalla, rango, x, y, fuente):
    """Dibuja una insignia llamativa para el rango (S+, S, A, B, C, F)."""
    colores_rango = {
        "S+": cfg.NEON_DORADO,
        "S": cfg.NEON_CYAN,
        "A": cfg.NEON_VERDE,
        "B": (100, 180, 255),
        "C": (230, 200, 100),
        "F": cfg.NEON_ROJO,
    }
    color = colores_rango.get(rango, cfg.GRIS_CLARO)
    rect = pygame.Rect(x - 24, y - 18, 48, 36)
    pygame.draw.rect(pantalla, (*color, 40) if len(color) == 3 else color, rect, border_radius=8)
    pygame.draw.rect(pantalla, color, rect, width=2, border_radius=8)

    img = fuente.render(rango, True, color)
    r_img = img.get_rect(center=rect.center)
    pantalla.blit(img, r_img)
