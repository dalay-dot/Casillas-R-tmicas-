import json
from pathlib import Path
import configuracion as cfg


class GestorDatos:
    def __init__(self):
        self.ruta = Path(__file__).resolve().parent / cfg.ARCHIVO_DATOS
        self.datos = {
            "records": {},  # "id_cancion": {"puntos": 0, "combo": 0, "rango": "-", "estrellas": 0}
            "ajustes": {
                "volumen_musica": 0.7,
                "volumen_sfx": 0.8,
                "silencio": False,
                "vibracion": True,
            },
            "estadisticas": {
                "partidas_jugadas": 0,
                "notas_perfectas": 0,
                "notas_totales": 0,
            },
        }
        self.cargar()

    def cargar(self):
        if self.ruta.exists():
            try:
                with open(self.ruta, "r", encoding="utf-8") as f:
                    cargado = json.load(f)
                    if isinstance(cargado, dict):
                        # Mezclar asegurando claves por defecto
                        for k, v in cargado.items():
                            if isinstance(v, dict) and k in self.datos:
                                self.datos[k].update(v)
                            else:
                                self.datos[k] = v
            except Exception:
                pass

    def guardar(self):
        try:
            with open(self.ruta, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def obtener_record(self, id_cancion):
        return self.datos["records"].get(
            id_cancion, {"puntos": 0, "combo": 0, "rango": "F", "estrellas": 0}
        )

    def actualizar_record(self, id_cancion, puntos, combo, rango, estrellas):
        actual = self.obtener_record(id_cancion)
        nuevo_record = False

        if puntos > actual.get("puntos", 0):
            nuevo_record = True
            actual["puntos"] = puntos

        actual["combo"] = max(actual.get("combo", 0), combo)
        
        # Comparar rangos para guardar el mejor
        jerarquia_rangos = {"S+": 5, "S": 4, "A": 3, "B": 2, "C": 1, "F": 0, "-": -1}
        if jerarquia_rangos.get(rango, 0) > jerarquia_rangos.get(actual.get("rango", "-"), -1):
            actual["rango"] = rango

        actual["estrellas"] = max(actual.get("estrellas", 0), estrellas)
        self.datos["records"][id_cancion] = actual
        self.guardar()
        return nuevo_record

    def registrar_partida(self, perfects, total_notas):
        self.datos["estadisticas"]["partidas_jugadas"] += 1
        self.datos["estadisticas"]["notas_perfectas"] += perfects
        self.datos["estadisticas"]["notas_totales"] += total_notas
        self.guardar()
