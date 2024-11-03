#!/bin/bash

set -e

OLD_DIR=$(pwd)

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $SCRIPT_DIR

cd dafny
make exe
cd Source/DafnyLanguageServer
dotnet build

cd ../../..

cd ide-vscode
npm install
npm run compile

cd ..

cd $OLD_DIR
