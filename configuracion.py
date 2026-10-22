import pygame

# Dimensiones de la ventana (Estilo Arcade Moderno / Vertical)
ANCHO = 520
ALTO = 840
FPS = 60
TITULO = "Casillas Rítmicas - Piano Tiles Edition"

# Pista de juego y carriles
CARRILES = 4
ANCHO_CARRIL = ANCHO // CARRILES
INICIO_PISTA = 130
ALTO_PISTA = ALTO - INICIO_PISTA - 80

# Línea de impacto y zona de acierto
LINEA_IMPACTO = 680
ALTO_BLOQUE = 110

# Ventanas de tolerancia para juicio de precisión (en píxeles de distancia al centro)
ZONA_PERFECT = 32
ZONA_GREAT = 65
ZONA_GOOD = 100

# Puntuaciones por precisión
PUNTOS_PERFECT = 300
PUNTOS_GREAT = 150
PUNTOS_GOOD = 60

# Sistema de Vida (HP)
HP_MAXIMO = 100.0
HP_INICIAL = 100.0
HP_PERFECT = 3.5
HP_GREAT = 1.8
HP_GOOD = 0.8
HP_FALLO = -16.0  # Penalización por dejar pasar un bloque o tocar fuera de tiempo
HP_DRENAJE_SOSTENIDO = -12.0

# Velocidad de caída (píxeles por segundo)
VELOCIDAD_DEFAULT = 400
VELOCIDAD_MINIMA = 280
VELOCIDAD_MAXIMA = 750

# Teclas por defecto (A, S, D, F)
TECLAS_DEFAULT = [
    pygame.K_a,
    pygame.K_s,
    pygame.K_d,
    pygame.K_f,
]
ETIQUETAS_TECLAS = ["A", "S", "D", "F"]

# Paleta de Colores Ultra-Moderna (Cyber / Neon / Dark Glass)
FONDO = (10, 13, 22)
FONDO_PANEL = (17, 23, 38)
FONDO_PISTA = (14, 18, 30)

CARRIL_A = (18, 24, 40)
CARRIL_B = (22, 29, 48)
LINEA_DIVISORIA = (38, 48, 76)

# Acentos y Neones
NEON_CYAN = (0, 242, 254)
NEON_MAGENTA = (255, 45, 140)
NEON_PURPLE = (138, 75, 255)
NEON_DORADO = (255, 215, 0)
NEON_VERDE = (0, 230, 118)
NEON_ROJO = (255, 68, 68)

BLANCO = (250, 252, 255)
GRIS_CLARO = (185, 195, 215)
GRIS_MEDIO = (110, 122, 148)
GRIS_OSCURO = (45, 52, 72)

# Colores de las casillas rítmicas
COLOR_BLOQUE = (28, 36, 60)
COLOR_BLOQUE_BORDE = (0, 242, 254)
COLOR_BLOQUE_SOSTENIDO = (138, 75, 255)

# Archivo de persistencia de récords
ARCHIVO_DATOS = "datos_juego.json"