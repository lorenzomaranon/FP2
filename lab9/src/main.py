from __future__ import annotations

from pathlib import Path

from laboratorio9_app import Laboratorio9App


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    app = Laboratorio9App(base_dir.parent / "data", base_dir)
    app.ejecutar()


if __name__ == "__main__":
    main()
