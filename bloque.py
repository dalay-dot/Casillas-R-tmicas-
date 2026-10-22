import pygame
import configuracion as cfg


class Bloque:
    def __init__(self, carril):
        self.carril = carril
        self.y = float(cfg.INICIO_PISTA - cfg.ALTO_BLOQUE)

    @property
    def centro_y(self):
        return self.y + cfg.ALTO_BLOQUE / 2

    def actualizar(self, segundos, velocidad):
        self.y += velocidad * segundos

    def esta_en_zona(self):
        distancia = abs(self.centro_y - cfg.LINEA_IMPACTO)
        return distancia <= cfg.TOLERANCIA

    def se_paso(self):
        limite = cfg.LINEA_IMPACTO + cfg.TOLERANCIA
        return self.centro_y > limite

    def dibujar(self, pantalla):
        x = self.carril * cfg.ANCHO_CARRIL + 9

        rectangulo = pygame.Rect(
            x,
            round(self.y),
            cfg.ANCHO_CARRIL - 18,
            cfg.ALTO_BLOQUE,
        )

        pygame.draw.rect(
            pantalla,
            cfg.BLOQUE,
            rectangulo,
            border_radius=10,
        )

        brillo = pygame.Rect(
            x + 10,
            round(self.y) + 10,
            cfg.ANCHO_CARRIL - 38,
            5,
        )

        pygame.draw.rect(
            pantalla,
            cfg.ACENTO,
            brillo,
            border_radius=2,
        )