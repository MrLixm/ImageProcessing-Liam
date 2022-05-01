"""
Constants
"""
from pathlib import Path

NAME = "OCIOexperiments"
ABR = "ocex"

DEV_DIR: Path = Path(__file__).parent.parent / "dev"
"""
Directory where you can find development resources
"""

OUTPUT_DIR: Path = DEV_DIR / "_outputs"
"""
Directory where you can write images.
Not versioned controled.
"""

DATA_DIR: Path = DEV_DIR / "data"
"""
Directory where you can find inputs for processing.
"""
