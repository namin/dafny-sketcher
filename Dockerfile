# syntax=docker/dockerfile:1

# Image for the QUICKSTART.md / VFP workflow: the forked Dafny toolchain, the
# Dafny Sketcher CLI, and a Python environment for the benchmark scripts.
#
# This builds for the host architecture by default and supports both
# linux/amd64 (Intel/AMD) and linux/arm64 (Apple Silicon, ARM Linux).
#
# Build (native to your machine):
#   docker build -t dafny-sketcher .
# Build for a specific architecture (buildx; --load imports into local Docker):
#   docker buildx build --platform linux/arm64 --load -t dafny-sketcher .
#   docker buildx build --platform linux/amd64 --load -t dafny-sketcher .
# Run (LLM key passed at runtime, per QUICKSTART step 3):
#   docker run --rm -it -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY dafny-sketcher

FROM mcr.microsoft.com/dotnet/sdk:8.0

ENV DEBIAN_FRONTEND=noninteractive

# Populated automatically by BuildKit ("amd64" or "arm64"); selects the z3 build.
ARG TARGETARCH

# The forked Dafny (namin:sketcher) recorded as the `dafny` submodule. The
# commit is pinned to what this repo currently references; override with
# --build-arg if the submodule pointer moves.
ARG DAFNY_REPO=https://github.com/namin/dafny.git
ARG DAFNY_COMMIT=c7aee04bf4004774da35598b9ffbdc1c7f752b24

RUN apt-get update && apt-get install -y --no-install-recommends \
        git make python3 python3-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Fetch the forked Dafny at the pinned submodule commit (the empty local
# `dafny/` dir is intentionally excluded via .dockerignore).
RUN git init dafny \
    && cd dafny \
    && git remote add origin "${DAFNY_REPO}" \
    && git fetch --depth 1 origin "${DAFNY_COMMIT}" \
    && git checkout FETCH_HEAD

# Sketcher sources from this repo.
COPY cli ./cli
COPY vfp ./vfp
COPY compile.sh README.md QUICKSTART.md ./

# Java is not installed, so stub the runtime jar to let `make exe` succeed
# (mirrors the fallback in compile.sh).
RUN mkdir -p dafny/Source/DafnyRuntime/DafnyRuntimeJava/build/libs \
             dafny/DafnyRuntimeJava/build/libs \
    && touch dafny/Source/DafnyRuntime/DafnyRuntimeJava/build/libs/DafnyRuntime-4.11.1.jar \
             dafny/DafnyRuntimeJava/build/libs/DafnyRuntime-4.11.1.jar

# Build the Dafny executable (also downloads z3 into Binaries).
RUN cd dafny && make exe

# Some builds place Dafny.dll under net8.0/; expose it where callers expect it.
RUN if [ ! -f dafny/Binaries/Dafny.dll ] && [ -f dafny/Binaries/net8.0/Dafny.dll ]; then \
        ln -s net8.0/Dafny.dll dafny/Binaries/Dafny.dll; \
    fi

# `make exe` does not fetch the solver, so download z3 into Binaries/z3/bin
# (Dafny's default lookup expects the file z3/bin/z3-4.12.1).
#   - amd64: `make z3-ubuntu` grabs the exact x64 builds (4.12.1 + 4.14.1) the
#     benchmarks were validated against.
#   - arm64: neither dafny-lang/solver-builds nor upstream z3 ship an arm64
#     *Linux* 4.12.1, so use the official arm64-glibc z3 4.14.1 and expose it
#     under the z3-4.12.1 name Dafny looks for.
ARG Z3_ARM64_URL=https://github.com/Z3Prover/z3/releases/download/z3-4.14.1/z3-4.14.1-arm64-glibc-2.34.zip
RUN apt-get update && apt-get install -y --no-install-recommends wget unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && cd dafny \
    && if [ "$TARGETARCH" = "arm64" ]; then \
         mkdir -p Binaries/z3/bin \
         && tmp="$(mktemp -d)" \
         && wget -q -O "$tmp/z3.zip" "$Z3_ARM64_URL" \
         && unzip -q "$tmp/z3.zip" -d "$tmp" \
         && cp "$tmp"/z3-*/bin/z3 Binaries/z3/bin/z3-4.14.1 \
         && cp "$tmp"/z3-*/bin/libz3.so Binaries/z3/bin/ 2>/dev/null || true \
         && ln -sf z3-4.14.1 Binaries/z3/bin/z3-4.12.1 \
         && chmod +x Binaries/z3/bin/z3-4.14.1 \
         && rm -rf "$tmp" ; \
       else \
         make z3-ubuntu ; \
       fi

# Build the Sketcher CLI (references the Dafny projects fetched above).
RUN cd cli && dotnet build DafnySketcherCli.csproj -c Release

# Python environment for the VFP benchmark scripts.
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --no-cache-dir \
        joblib tqdm anthropic google-genai openai ollama

# `dafny` and `dafny-sketcher-cli` launchers on PATH (the scripts invoke both).
RUN printf '#!/bin/sh\nexec dotnet /app/dafny/Binaries/Dafny.dll "$@"\n' \
        > /usr/local/bin/dafny \
    && printf '#!/bin/sh\nexec dotnet /app/cli/bin/Release/net8.0/DafnySketcherCli.dll "$@"\n' \
        > /usr/local/bin/dafny-sketcher-cli \
    && chmod 755 /usr/local/bin/dafny /usr/local/bin/dafny-sketcher-cli

# Expose the venv's python/pip in /usr/local/bin so they resolve in every shell,
# including login shells (`bash -l`) that rebuild PATH from /etc/profile.
RUN for t in python python3 pip pip3; do \
        printf '#!/bin/sh\nexec /opt/venv/bin/%s "$@"\n' "$t" > "/usr/local/bin/$t" \
        && chmod 755 "/usr/local/bin/$t"; \
    done

# Where sketcher.py looks for the CLI (QUICKSTART step 2b).
ENV DAFNY_SKETCHER_CLI_DLL_PATH=/app/cli/bin/Release/net8.0/DafnySketcherCli.dll

# Optional caching, recommended for benchmark reruns (QUICKSTART step 3).
ENV CACHE_LLM=1 \
    CACHE_DAFNY=1

WORKDIR /app/vfp
CMD ["/bin/bash"]
