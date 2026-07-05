# gcp-diagram-generator (draw.io backend)

Generate [draw.io](https://app.diagrams.net) architecture diagrams from
Google Cloud [Asset Inventory](https://cloud.google.com/asset-inventory/docs/overview)
export snapshots.

This is one of two diagram backends in this repo — see [`../graphviz`](../graphviz)
for the alternative that renders via the `diagrams`/Graphviz stack instead.
Nodes use the same official GCP service icons as draw.io's own built-in "GCP"
shape library (extracted from app.diagrams.net's bundled icon set), so the
diagram looks like a hand-drawn GCP architecture diagram while still being
fully editable XML that opens directly in app.diagrams.net.

## Project structure

```
drawio/
├── src/gcp_diagram_generator/   # Package source
│   ├── cli.py                  # Command-line entry point
│   ├── loader.py                # JSONL snapshot loading
│   ├── categories.py             # assetType -> diagram category/icon mapping
│   ├── gcp_icons.py               # Base64 GCP icon SVGs, keyed by icon name
│   ├── graph.py                  # Builds the node/edge graph model
│   └── drawio.py                 # Renders the graph model as mxGraph (.drawio) XML
├── output/                       # Generated .drawio files (gitignored)
└── tests/                        # Unit tests
```

Sample input snapshots live in [`../mock-data/asset-inventory/`](../mock-data/asset-inventory),
shared with the graphviz backend.

## Input format

Each file under `../mock-data/asset-inventory/` is newline-delimited JSON
(one `google.cloud.asset.v1.Asset` object per line), matching the real
output of `gcloud asset export --content-type=<TYPE>`.

Which content types are read is controlled by `--content-types`
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
- No third-party runtime dependencies — the generator only uses the
  standard library (`json`, `xml.etree.ElementTree`, `argparse`, `pathlib`).
  `pytest` is only needed if you want to run the test suite (installed via
  the `dev` extra below).

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

Run from the `drawio/` directory:

```bash
gcp-diagram-generator \
  --input-dir ../mock-data/asset-inventory \
  --output-dir output \
  --output-name gcp-architecture.drawio \
  --content-types resource,relationship
```

To also pull in IAM/org-policy/OS annotations and Access Context Manager
nodes:

```bash
gcp-diagram-generator --content-types resource,relationship,iam-policy,org-policy,access-policy,os-inventory
```

Or without installing the package:

```bash
python -m gcp_diagram_generator.cli --input-dir ../mock-data/asset-inventory
```

The generated file can be opened directly in
[app.diagrams.net](https://app.diagrams.net) via File → Open, or dragged
into the browser tab.

## Tests

```bash
python -m pytest tests/
```
