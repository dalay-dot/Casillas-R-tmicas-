import pygame

# Ventana
ANCHO = 480
ALTO = 760
FPS = 60
TITULO = "Casillas Rítmicas"

# Área de juego
CARRILES = 4
ANCHO_CARRIL = ANCHO // CARRILES
INICIO_PISTA = 120

# Bloques
ALTO_BLOQUE = 100
VELOCIDAD_INICIAL = 250
AUMENTO_VELOCIDAD = 25
VELOCIDAD_MAXIMA = 550

# Tiempo entre bloques, en segundos
INTERVALO_BLOQUES = 0.65

# Zona de impacto:
# el centro del bloque debe estar cerca de esta línea.
LINEA_IMPACTO = 630
TOLERANCIA = 42

# Teclas de izquierda a derecha
TECLAS = [
    pygame.K_d,
    pygame.K_f,
    pygame.K_j,
    pygame.K_k,
]

ETIQUETAS = ["D", "F", "J", "K"]

# Colores
FONDO = (14, 17, 29)
PANEL = (25, 30, 48)
CARRIL_CLARO = (228, 233, 244)
CARRIL_OSCURO = (210, 219, 236)
BLOQUE = (22, 27, 44)
BLANCO = (245, 247, 255)
GRIS = (164, 175, 199)
ACENTO = (70, 225, 191)
ROJO = (255, 105, 125)