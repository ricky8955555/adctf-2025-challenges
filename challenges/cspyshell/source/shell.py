import os
import sys
import zipfile


def main() -> None:
    fd = int(sys.argv[1])

    with zipfile.ZipFile(__loader__.archive, "r") as zip:
        dll = zip.read("core.dll")

    os.write(fd, dll)


if __name__ == "__main__":
    main()
