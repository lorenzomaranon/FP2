from __future__ import annotations

from pathlib import Path

from laboratorio10_app import Laboratorio10App


def main() -> None:
    raiz = Path(__file__).resolve().parents[2]
    app = Laboratorio10App(
        lab9_data_dir=raiz / "lab9" / "data",
        lab10_data_dir=raiz / "lab10" / "data",
    )
    app.ejecutar()


if __name__ == "__main__":
    main()
