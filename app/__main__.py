"""
This module is called when the package is executed as a module.
"""

import sys


if __name__ == "__main__":
    from app.main import main

    sys.exit(main())
