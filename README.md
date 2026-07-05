# gcp-diagram-generator

Generate architecture diagrams from Google Cloud
[Asset Inventory](https://cloud.google.com/asset-inventory/docs/overview)
export snapshots. Two independent backends are provided, sharing the same
mock input data:

- [`drawio/`](drawio) — emits editable [draw.io](https://app.diagrams.net)
  mxGraph XML using the same official GCP icons as draw.io's own built-in
  shape library. Opens directly in app.diagrams.net for further editing.
- [`graphviz/`](graphviz) — emits a static PNG/SVG/PDF styled with real GCP
  service icons, using the [`diagrams`](https://github.com/mingrammer/diagrams)
  library (renders via Graphviz).

Each backend is its own installable Python package with its own
`pyproject.toml`, virtualenv, and tests — see the README in each folder for
setup and usage.

## Project structure

```
.
├── mock-data/asset-inventory/   # Shared sample Cloud Asset Inventory snapshots
│   ├── resource.json
│   ├── iam-policy.json
│   ├── org-policy.json
│   ├── access-policy.json
│   ├── os-inventory.json
│   └── relationship.json
├── drawio/                      # draw.io (mxGraph XML) backend
└── graphviz/                    # GCP-icon (diagrams/Graphviz) backend
```

## Input format

Each file under `mock-data/asset-inventory/` is newline-delimited JSON (one
`google.cloud.asset.v1.Asset` object per line), matching the real output of
`gcloud asset export --content-type=<TYPE>`. Both backends currently read
two content types:

- `resource.json` — one node per resource
- `relationship.json` — edges between resources (e.g. instance → network)
