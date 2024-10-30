import os


def voluseg_update() -> None:
    """Shortcut to update package."""
    os.system(
        "pip install --upgrade --force-reinstall git+https://github.com/mikarubi/voluseg.git"
    )
