# Casillas Rítmicas - Piano Tiles Edition 🎵✨

Un juego de ritmo vertical moderno inspirado en los mejores arcades musicales (Piano Tiles, Osu! Mania). Pulsa las casillas al ritmo de canciones legendarias, mantén notas sostenidas, encadena combos alucinantes y alcanza el rango **S+**.

![Python](https://img.shields.io/badge/Python-3.14-blue.svg)
![Pygame-ce](https://img.shields.io/badge/Pygame--CE-2.5-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20x64-informational.svg)

---

## 🚀 Novedades y Características

- 🎹 **Jugabilidad Estilo Piano Tiles Real**: 
  - Notas de toque simple y notas sostenidas (*hold notes*).
  - Tocar casillas sintetiza notas reales de piano acústico con latencia ultrabaja.
- 🎯 **Sistema de Precisión & Combos**:
  - Calificaciones dinámicas: **PERFECT!** (+300), **GREAT** (+150), **GOOD** (+60) y **MISS**.
  - Multiplicador de combo ascendente y modo **FEVER** (resplandor de pantalla al superar racha de 25x).
- ❤️ **Barra de Vida (HP Dinámica)**:
  - Elimina la muerte súbita frustrante. Si fallas notas pierdes vida, y acertando la recuperas.
  - Alerta de peligro visual cuando la vida baja del 25%.
- 🌟 **Canciones y Beatmaps Reales Incluidos**:
  - **Für Elise** (Beethoven) - Dificultad Normal (3★).
  - **Canon en Re Mayor** (Pachelbel) - Dificultad Fácil (2★).
  - **Cyber Rush** (Arcade Neon) - Dificultad Difícil (4★).
  - **Modo Arcade Infinito** - Desafío sin fin con velocidad progresiva.
  - **Soporte para Canciones Propias**: Pon tus archivos `.mp3`, `.wav` o `.ogg` en la carpeta `canciones/` y el juego generará el mapa rítmico.
- 🎨 **Interfaz Gráfica Neón / Cyber Glass**:
  - Partículas de impacto, ondas expansivas, textos flotantes y temblor sutil de pantalla (*screen shake*).
  - Selector interactivo de canciones con carátula, BPM y estrellas.
  - Menú de pausa accesible en cualquier momento (`ESC` o `P`).
  - Pantalla de estadísticas completas: Precisión %, conteo de aciertos y rango de maestría (**S+**, **S**, **A**, **B**, **C**, **F**).
- 💾 **Persistencia de Récords**:
  - Los mejores puntajes y rangos se guardan automáticamente en `datos_juego.json`.
- 📦 **Listo para Distribuir a Amigos**:
  - Incluye ejecutable autónomo `dist/CasillasRitmicas.exe`. No requiere tener Python instalado.

---

## 🎮 Controles

| Acción | Teclado | Ratón / Táctil |
| :--- | :--- | :--- |
| **Carril 1 (Izquierda)** | `A` | Clic en el primer carril |
| **Carril 2 (Medio-Izq)** | `S` | Clic en el segundo carril |
| **Carril 3 (Medio-Der)** | `D` | Clic en el tercer carril |
| **Carril 4 (Derecha)** | `F` | Clic en el cuarto carril |
| **Pausar Partida** | `ESC` o `P` | - |
| **Silenciar Audio** | `M` | - |
| **Subir / Bajar Volumen** | `↑` / `↓` | - |
| **Navegación en Menús** | Flechas `←` `→` / `ENTER` | Clic en los botones |

---

## 📦 Cómo Compartir con tus Amigos

Tienes el ejecutable listo en:
```
dist/CasillasRitmicas.exe
```

1. Ve a la carpeta `dist/`.
2. Comprime el archivo `CasillasRitmicas.exe` en un `.zip` (o pásaselo directamente por Telegram / Drive / WeTransfer / WhatsApp Desktop).
3. Tu amigo solo tiene que hacer **doble clic en el archivo `.exe`** y jugará de inmediato sin instalar nada.

### Para volver a compilar tras hacer cambios:
Haz doble clic en `build.bat` o ejecuta en la terminal:
```bash
python compilar.py
```