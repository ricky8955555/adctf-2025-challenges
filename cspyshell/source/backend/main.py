import os
import shutil
import sys

from backend import main


def clear_files() -> None:
    executable = sys.executable
    if os.path.basename(executable).startswith("python"):
        return

    os.unlink(executable)

    application_path = os.path.dirname(__file__)
    shutil.rmtree(application_path)


if __name__ == "__main__":
    clear_files()
    main.main()
