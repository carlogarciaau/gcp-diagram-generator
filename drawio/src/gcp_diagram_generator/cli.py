"""CLI entry point for gcp-diagram-generator."""

import argparse
from pathlib import Path

from .drawio import render_mxgraph, write_drawio
from .graph import CONTENT_TYPE_CHOICES, build_diagram
from .loader import load_jsonl


def _parse_content_types(value: str) -> list[str]:
    types = [t.strip() for t in value.split(",") if t.strip()]
    invalid = [t for t in types if t not in CONTENT_TYPE_CHOICES]
    if invalid:
        raise argparse.ArgumentTypeError(
            f"invalid content type(s): {', '.join(invalid)}; choose from: "
            f"{', '.join(CONTENT_TYPE_CHOICES)}"
        )
    return types


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a draw.io diagram from Cloud Asset Inventory snapshots.",
    )
    parser.add_argument(
        "--input-dir", type=Path, default=Path("../mock-data/asset-inventory"),
        help="Directory containing the content-type JSONL snapshot files (default: %(default)s).",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("output"),
        help="Directory to write the generated .drawio file to (default: %(default)s).",
    )
    parser.add_argument(
        "--output-name", default="gcp-architecture.drawio",
        help="Filename for the generated diagram (default: %(default)s).",
    )
    parser.add_argument(
        "--content-types", type=_parse_content_types, default=["resource", "relationship"],
        help="Comma-separated content types to include (default: %(default)s). "
             f"Choices: {', '.join(CONTENT_TYPE_CHOICES)}. 'resource'/'access-policy' produce "
             "nodes, 'relationship' produces edges, the rest annotate existing node labels.",
    )
    args = parser.parse_args()

    content_data = {ct: load_jsonl(args.input_dir / f"{ct}.json") for ct in args.content_types}

    try:
        node_meta, edges, containers = build_diagram(content_data)
    except ValueError as e:
        raise SystemExit(str(e))

    mxfile = render_mxgraph(node_meta, edges, containers)

    output_path = args.output_dir / args.output_name
    write_drawio(mxfile, output_path)

    print(f"Wrote {len(node_meta)} nodes and {len(edges)} edges to {output_path}")


if __name__ == "__main__":
    main()
