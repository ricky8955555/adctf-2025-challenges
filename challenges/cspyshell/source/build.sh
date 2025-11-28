#!/bin/bash

set -e

DOTNET_VERSION="net8.0"
RUNTIME_IDENTIFIER="linux-x64"

BINPACK_IV="110,73,99,48,78,49,107,111,55,105,45,112,51,114,82,35"

PYTHON_EXECUTABLE="python3.12"

if [ -d build ]; then
    echo "build directory already exists. if you want to rebuild it, remove it and run the script again."
    exit 1
fi

rm -rf dist
mkdir build dist

cd build

cp -R ../frontend frontend

$PYTHON_EXECUTABLE -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt

mkdir backend
cd backend
pyinstaller -F -n backend ../../backend/main.py

mkdir -p ../frontend/Cspyshell.Frontend.Core/res
cp dist/backend ../frontend/Cspyshell.Frontend.Core/res/backend

cd ../frontend
dotnet publish

python3 ../../scripts/binpack.py pack $BINPACK_IV Cspyshell.Frontend.Core/bin/Release/$DOTNET_VERSION/$RUNTIME_IDENTIFIER/publish/Cspyshell.Frontend.Core.dll ../core.dll
cp Cspyshell.Frontend.Shell/bin/Release/$DOTNET_VERSION/$RUNTIME_IDENTIFIER/publish/Cspyshell.Frontend.Shell ../shell

cd ../
cp ../shell.py __main__.py

zip shell.zip __main__.py core.dll
cat shell shell.zip > ../dist/cspyshell

cp frontend/Cspyshell.Frontend.Core/bin/Release/$DOTNET_VERSION/$RUNTIME_IDENTIFIER/publish/libsodium.so ../dist/

chmod +x ../dist/cspyshell
