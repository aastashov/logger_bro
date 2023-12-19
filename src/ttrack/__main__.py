#!/usr/bin/env python3
import os
import sys

from __version__ import __version__
from console.application import get_application


def main() -> int:
    app = get_application(__version__)
    return app.run()


if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_path, "tracker"))
    sys.exit(main())
