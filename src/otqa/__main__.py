"""Run the same lightweight command entry point as the installed otqa script."""
from .cli import main

if __name__ == '__main__':
    raise SystemExit(main())
