# gcp-diagram-generator (graphviz backend)

Generate architecture diagrams with real GCP service icons from Cloud
[Asset Inventory](https://cloud.google.com/asset-inventory/docs/overview)
export snapshots, using the [`diagrams`](https://github.com/mingrammer/diagrams)
Python library (which renders via Graphviz).

This is one of two diagram backends in this repo — see [`../drawio`](../drawio)
for the alternative that emits editable mxGraph XML for app.diagrams.net.
This backend produces a static image (PNG/SVG/PDF) styled like an official
Google Cloud architecture diagram, but it is not interactively editable
afterward.

## Project structure

```
graphviz/
├── src/gcp_diagram_generator_graphviz/
│   ├── cli.py       # Command-line entry point
│   ├── loader.py     # JSONL snapshot loading
│   ├── icon_map.py    # assetType -> diagrams.gcp icon class/category mapping
│   ├── graph.py        # Builds the node/edge graph model
│   └── render.py        # Renders the graph model via diagrams/Graphviz
├── output/              # Generated diagram images (gitignored)
└── tests/                # Unit tests
```

Sample input snapshots live in [`../mock-data/asset-inventory/`](../mock-data/asset-inventory),
shared with the drawio backend.

## Input format

Same as the drawio backend: newline-delimited JSON asset snapshots. Which
content types are read is controlled by `--content-types`
(default: `resource,relationship`):

| Content type | Effect |
| --- | --- |
| `resource` | One node per resource. |
| `access-policy` | Adds AccessPolicy/AccessLevel/ServicePerimeter as additional nodes, with containment edges and ServicePerimeter → protected-resource edges. |
| `relationship` | Edges between existing nodes (e.g. instance → network). |
| `iam-policy` | Annotates existing nodes' labels with an IAM binding count. |
| `org-policy` | Annotates existing nodes' labels with an org policy constraint count. |
| `os-inventory` | Annotates existing nodes' labels with OS name/version. |

At least one of `resource`/`access-policy` must be selected, since those are
the only content types that produce nodes.

## Prerequisites

- Python 3.10+
- pip
- **Graphviz system binary** (`dot`) — required by the `diagrams` package to
  render images. Install it via your OS package manager, e.g.:
  ```bash
  brew install graphviz        # macOS
  apt-get install graphviz     # Debian/Ubuntu
  ```
- `pytest` is only needed to run the test suite (installed via the `dev`
  extra below).

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

Run from the `graphviz/` directory:

```bash
gcp-diagram-generator-graphviz \
  --input-dir ../mock-data/asset-inventory \
  --output-dir output \
  --output-name gcp-architecture \
  --format png \
  --content-types resource,relationship
```

To also pull in IAM/org-policy/OS annotations and Access Context Manager
nodes:

```bash
gcp-diagram-generator-graphviz --content-types resource,relationship,iam-policy,org-policy,access-policy,os-inventory
```

Or without installing the package:

```bash
python -m gcp_diagram_generator_graphviz.cli --input-dir ../mock-data/asset-inventory
```

## Tests

```bash
python -m pytest tests/
```
