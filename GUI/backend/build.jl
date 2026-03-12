"""
Build script for NT Cycling Model – compiles the Julia backend into a
standalone executable using PackageCompiler.jl.

Usage (from repo root):
    julia --project=GUI/backend/build GUI/backend/build.jl

Prerequisites:
  1. Julia 1.10+ installed and on PATH.
  2. Backend dependencies resolved:
       julia --project=GUI/backend -e 'using Pkg; Pkg.instantiate()'
  3. PackageCompiler installed in the build env:
       julia --project=GUI/backend/build -e 'using Pkg; Pkg.instantiate()'

Output: GUI/backend/julia-app/
  bin/server        – compiled executable
  lib/              – Julia runtime + precompiled sysimage
  share/            – Julia standard library sources

The julia-app/ directory is then bundled by electron-builder as an
extraResource inside the Electron app (see GUI/electron/package.json).
"""

using PackageCompiler

backend_dir = joinpath(@__DIR__)          # GUI/backend/
output_dir  = joinpath(@__DIR__, "julia-app")
precompile  = joinpath(@__DIR__, "precompile_app.jl")

@info "Building NT Cycling app..." backend_dir output_dir

create_app(
    backend_dir,
    output_dir;
    precompile_execution_file = precompile,
    force = true,
    include_lazy_artifacts = true,
)

@info "Build complete." output_dir
