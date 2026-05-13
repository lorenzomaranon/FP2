import numpy as np
import sys
from pathlib import Path

# Cargar la ruta de retos igual que en tu script principal
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
retos_path = project_root / "data" / "win_314" / "dist"
if retos_path.exists():
    sys.path.insert(0, str(retos_path))

import retos_optimizacion as reto

class Funcion_8(reto._BaseOpt):
    def __init__(self):
        shift_vectors = [0.0] * 10
        super().__init__(shift_vectors)

    def evaluar(self, x):
        z = self._preparar_x(x)
        z = z - self._shift
        sum_term = np.sum(z * np.sin(np.sqrt(np.abs(z))))
        return float(418.9828872724338 * self._dims - sum_term)

class Funcion_8_modificada(reto._BaseOpt):
    def __init__(self):
        shift_vectors = [-419.9687] * 10
        super().__init__(shift_vectors)

    def evaluar(self, x):
        z = self._preparar_x(x)
        z = z - self._shift
        sum_term = np.sum(z * np.sin(np.sqrt(np.abs(z))))
        return float(418.9828872724338 * self._dims - sum_term)