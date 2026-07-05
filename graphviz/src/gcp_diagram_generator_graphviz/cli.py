"""CLI entry point for gcp-diagram-generator-graphviz."""

import argparse
from pathlib import Path

from .graph import CONTENT_TYPE_CHOICES, build_diagram
from .loader import load_jsonl
from .render import render_diagram


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
        description="Generate a GCP-icon architecture diagram from Cloud Asset Inventory "
                    "snapshots, using the diagrams/Graphviz stack.",
    )
    parser.add_argument(
        "--input-dir", type=Path, default=Path("../mock-data/asset-inventory"),
        help="Directory containing the content-type JSONL snapshot files (default: %(default)s).",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("output"),
        help="Directory to write the generated diagram to (default: %(default)s).",
    )
    parser.add_argument(
        "--output-name", default="gcp-architecture",
        help="Filename (without extension) for the generated diagram (default: %(default)s).",
    )
    parser.add_argument(
        "--format", default="png", choices=["png", "svg", "pdf", "jpg"],
        help="Output image format (default: %(default)s).",
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
        node_meta, edges, box_tree = build_diagram(content_data)
    except ValueError as e:
        raise SystemExit(str(e))

    output_path = args.output_dir / args.output_name
    render_diagram(node_meta, edges, box_tree, output_path, output_format=args.format)

    print(f"Wrote {len(node_meta)} nodes and {len(edges)} edges to "
          f"{output_path.with_suffix('.' + args.format)}")


if __name__ == "__main__":
    main()
