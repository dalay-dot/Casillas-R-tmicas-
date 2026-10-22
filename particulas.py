import math
import random
import pygame
import configuracion as cfg


class Particula:
    def __init__(self, x, y, color, velocidad_max=180, vida=0.45):
        self.x = float(x)
        self.y = float(y)
        angulo = random.uniform(0, 2 * math.pi)
        rapidez = random.uniform(30, velocidad_max)
        self.vx = math.cos(angulo) * rapidez
        self.vy = math.sin(angulo) * rapidez - random.uniform(20, 60)
        self.color = color
        self.vida_total = vida
        self.vida = vida
        self.radio_inicial = random.uniform(3.0, 6.0)

    def actualizar(self, dt):
        self.vida -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Fricción suave
        self.vx *= 0.94
        self.vy *= 0.94

    @property
    def viva(self):
        return self.vida > 0

    def dibujar(self, pantalla):
        if not self.viva:
            return
        progreso = self.vida / self.vida_total
        radio = max(1, int(self.radio_inicial * progreso))
        alpha = int(255 * progreso)

        # Dibujo con superficie para soportar transparencia
        superficie = pygame.Surface((radio * 2 + 2, radio * 2 + 2), pygame.SRCALPHA)
        color_con_alpha = (*self.color, alpha)
        pygame.draw.circle(superficie, color_con_alpha, (radio + 1, radio + 1), radio)
        pantalla.blit(superficie, (round(self.x - radio), round(self.y - radio)))


class OndaImpacto:
    def __init__(self, x, y, color, radio_max=50, duracion=0.28):
        self.x = x
        self.y = y
        self.color = color
        self.radio_max = radio_max
        self.duracion = duracion
        self.tiempo = 0.0

    def actualizar(self, dt):
        self.tiempo += dt

    @property
    def viva(self):
        return self.tiempo < self.duracion

    def dibujar(self, pantalla):
        if not self.viva:
            return
        progreso = self.tiempo / self.duracion
        radio = int(self.radio_max * progreso)
        if radio <= 0:
            return
        alpha = int(255 * (1.0 - progreso))
        grosor = max(1, int(3 * (1.0 - progreso)))

        superficie = pygame.Surface((radio * 2 + 4, radio * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(
            superficie,
            (*self.color, alpha),
            (radio + 2, radio + 2),
            radio,
            width=grosor,
        )
        pantalla.blit(superficie, (round(self.x - radio - 2), round(self.y - radio - 2)))


class TextoFlotante:
    def __init__(self, texto, x, y, color, fuente, duracion=0.55):
        self.texto = texto
        self.x = x
        self.y = y
        self.color = color
        self.fuente = fuente
        self.duracion = duracion
        self.tiempo = 0.0

    def actualizar(self, dt):
        self.tiempo += dt
        self.y -= 35 * dt  # Flota hacia arriba

    @property
    def viva(self):
        return self.tiempo < self.duracion

    def dibujar(self, pantalla):
        if not self.viva:
            return
        progreso = self.tiempo / self.duracion
        alpha = int(255 * (1.0 - (progreso ** 1.8)))

        imagen = self.fuente.render(self.texto, True, self.color)
        imagen.set_alpha(alpha)
        rect = imagen.get_rect(center=(round(self.x), round(self.y)))
        pantalla.blit(imagen, rect)


class SistemaEfectos:
    def __init__(self):
        self.particulas = []
        self.ondas = []
        self.textos = []
        self.shake_tiempo = 0.0
        self.shake_magnitud = 0.0

    def trigger_shake(self, magnitud=5.0, duracion=0.18):
        self.shake_magnitud = magnitud
        self.shake_tiempo = duracion

    def agregar_explosion(self, x, y, color, cantidad=18):
        for _ in range(cantidad):
            self.particulas.append(Particula(x, y, color))
        self.ondas.append(OndaImpacto(x, y, color))

    def agregar_texto(self, texto, x, y, color, fuente):
        self.textos.append(TextoFlotante(texto, x, y, color, fuente))

    def actualizar(self, dt):
        if self.shake_tiempo > 0:
            self.shake_tiempo -= dt
            if self.shake_tiempo <= 0:
                self.shake_magnitud = 0.0

        for p in self.particulas:
            p.actualizar(dt)
        self.particulas = [p for p in self.particulas if p.viva]

        for o in self.ondas:
            o.actualizar(dt)
        self.ondas = [o for o in self.ondas if o.viva]

        for t in self.textos:
            t.actualizar(dt)
        self.textos = [t for t in self.textos if t.viva]

    def obtener_offset_shake(self):
        if self.shake_tiempo > 0:
            ox = random.uniform(-self.shake_magnitud, self.shake_magnitud)
            oy = random.uniform(-self.shake_magnitud, self.shake_magnitud)
            return ox, oy
        return 0, 0

    def dibujar(self, pantalla):
        for o in self.ondas:
            o.dibujar(pantalla)
        for p in self.particulas:
            p.dibujar(pantalla)
        for t in self.textos:
            t.dibujar(pantalla)
