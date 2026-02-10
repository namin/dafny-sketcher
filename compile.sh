#!/bin/bash

set -e

OLD_DIR=$(pwd)

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $SCRIPT_DIR

cd dafny
# Stub out the Java runtime jar if Java is not installed, so dotnet build succeeds
if ! command -v java &> /dev/null; then
  mkdir -p Source/DafnyRuntime/DafnyRuntimeJava/build/libs
  touch Source/DafnyRuntime/DafnyRuntimeJava/build/libs/DafnyRuntime-4.11.1.jar
  mkdir -p DafnyRuntimeJava/build/libs
  touch DafnyRuntimeJava/build/libs/DafnyRuntime-4.11.1.jar
fi
make exe
cd Source/DafnyLanguageServer
dotnet build

cd ../../..

cd ide-vscode
npm install
npm run compile

cd ..

cd cli
dotnet build DafnySketcherCli.csproj -c Release

cd ..

cd mcp
npm install
npm run build

cd ..

cd $OLD_DIR
