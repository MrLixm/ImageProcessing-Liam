"""
Constants
"""
from pathlib import Path

NAME = "pixelDataTesting"
ABR = "pxdt"

PACKAGE_DIR: Path = Path(__file__).parent
"""
Root diretcory for this package.
"""

DATA_DIR: Path = PACKAGE_DIR / "data"
"""
Directory where you can find pixels images and other disk dependencies
"""
