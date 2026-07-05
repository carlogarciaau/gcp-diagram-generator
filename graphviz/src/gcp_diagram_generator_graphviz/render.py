"""Render a node/edge/box-tree graph model as a GCP-icon diagram via `diagrams`/Graphviz."""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge


def _render_box(box: dict, node_meta: dict, diagram_nodes: dict) -> None:
    """Recursively render a box (Organization/Folder/Project) as a nested Cluster."""
    if not box["resources"] and not box["children"]:
        return
    with Cluster(box["title"]):
        for name in box["resources"]:
            meta = node_meta[name]
            diagram_nodes[name] = meta["icon_class"](meta["label"])
        for child in box["children"]:
            _render_box(child, node_meta, diagram_nodes)


def render_diagram(node_meta: dict, edges: list[tuple], box_tree: dict, output_path: Path,
                    output_format: str = "png") -> None:
    """Render node_meta/edges/box_tree to output_path (without extension applied twice).

    output_path should include the desired filename stem; diagrams appends
    the extension implied by output_format and creates parent directories
    as needed.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    stem = str(output_path.with_suffix(""))

    with Diagram(
        name="GCP Architecture", filename=stem, outformat=output_format,
        direction="TB", show=False,
    ):
        diagram_nodes = {}
        _render_box(box_tree["org_box"], node_meta, diagram_nodes)
        for folder_box in box_tree["folder_boxes"]:
            _render_box(folder_box, node_meta, diagram_nodes)

        for source, target, label in edges:
            if source in diagram_nodes and target in diagram_nodes:
                diagram_nodes[source] >> Edge(label=label or "") >> diagram_nodes[target]
