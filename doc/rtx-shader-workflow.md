# `rendererrtx` Shader Build + Reflection Workflow

This workflow covers `code/rendererrtx/shaders` only.

## Purpose

`RTX-M1-005` requires a deterministic shader compilation path with reflection metadata.

The canonical entrypoint is:

`code/rendererrtx/shaders/build_shaders.py`

It compiles all `rendererrtx` GLSL shader variants, then writes:

1. `code/rendererrtx/shaders/spirv/shader_data.c` (embedded SPIR-V byte arrays consumed by `vk.c`)
2. `code/rendererrtx/shaders/spirv/shader_reflection.json` (descriptor/push-constant reflection)

## Prerequisites

1. Python 3
2. `glslangValidator` from Vulkan SDK

`build_shaders.py` resolves `glslangValidator` in this order:

1. `--glslang <path>`
2. `GLSLANG_VALIDATOR` env var
3. `%VULKAN_SDK%/Bin/glslangValidator(.exe)`
4. `PATH`

## Usage

Run from repository root:

```bash
python code/rendererrtx/shaders/build_shaders.py
```

Windows wrapper:

```bat
code\rendererrtx\shaders\compile.bat
```

POSIX wrapper:

```sh
code/rendererrtx/shaders/compile.sh
```

Validate generated artifacts are up to date without writing:

```bash
python code/rendererrtx/shaders/build_shaders.py --check
```

## Determinism Rules

The builder is deterministic by construction:

1. Direct `.vert` and `.frag` files are compiled in stable sorted order.
2. Template permutations (`gen_*`, `light_*`) are emitted from an explicit fixed manifest.
3. Output symbol names are fixed and compatible with existing `vk.c` usage.
4. C array formatting is stable to avoid non-functional churn in `shader_data.c`.
5. Reflection JSON uses stable ordering for shader variants and descriptor bindings.

## Reflection Contents

`shader_reflection.json` includes per-shader:

1. Source file + stage + compile defines
2. Output SPIR-V byte size
3. Descriptor bindings:
   - set
   - binding
   - storage class
   - descriptor class (uniform buffer, storage buffer, combined image sampler, etc.)
   - descriptor count
4. Push-constant ranges (size in bytes)

This metadata is intended for validation and future pipeline-layout automation work.
