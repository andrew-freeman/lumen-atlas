# lumen-atlas

lumen-atlas is a graph-based framework for mapping, representing, and rendering emissive LEDs embedded in deformable, non-flat surfaces such as wearable volumetric displays.

Instead of treating LEDs as pixels on a grid or points on a rigid mesh, lumen-atlas models them as nodes in multiple overlapping graphs:

- electrical wiring adjacency
- surface proximity
- semantic regions defined by human understanding

This approach prioritizes topology, perception, and navigability over strict geometric accuracy.

## Why not a 2D matrix or 3D mesh?

Wearable and soft-body displays:

- deform continuously
- lack stable geometry
- rely on volumetric diffusion (e.g. fur, fabric)

A graph representation remains stable under deformation and enables expressive, organic effects without requiring precise spatial reconstruction.

## Core concepts

- **Node:** a single addressable LED with metadata
- **Edge sets:** different relationships between nodes (wiring, surface, semantic)
- **Atlas space:** a stable 2D parameterization used for indexing and navigation
- **Embedding:** optional 2D or 3D visualization derived from the graph

## Typical workflow

1. LEDs are activated sequentially or sparsely.
2. Camera-based detection estimates perceptual proximity.
3. Nodes are added to the atlas with rough coordinates and neighbors.
4. The graph is refined via iterative relaxation.
5. Effects are rendered by traversing graphs, not coordinates.

## Non-goals

- Precise physical simulation
- Real-time pose tracking
- Treating geometry as ground truth

lumen-atlas is designed to be hardware-agnostic, human-readable, and iteratively refined.

## Repository layout

- `schema/`: JSON schemas defining the atlas and node structures.
- `core/`: Python utilities for graph representation, queries, and embeddings.
- `tools/`: calibration and scanning tool placeholders.
- `data/`: example atlas data.
- `notes/`: working notes and mapping guidance.

## Getting started

- Inspect the schemas under `schema/` to understand the JSON shape expected for atlas data.
- Load `data/example_atlas.json` with the utilities in `core/` to experiment with graph operations.
- Extend the `tools/` folder with calibration or LED scanning scripts that fit your hardware pipeline.

## Principles and guidelines

- Prefer topology over geometry; treat embeddings as derived visualization aids.
- Keep data human-readable and semantic-rich to support iterative mapping.
- Keep hardware control separate from core representation logic.

