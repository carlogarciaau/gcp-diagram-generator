"""Render a node/edge/container graph model as draw.io (mxGraph) XML."""

import xml.etree.ElementTree as ET
from pathlib import Path


def render_mxgraph(node_meta: dict, edges: list[tuple], containers: list[dict]) -> ET.Element:
    mxfile = ET.Element("mxfile", host="app.diagrams.net")
    diagram = ET.SubElement(mxfile, "diagram", name="GCP Architecture", id="gcp-diagram")
    model = ET.SubElement(
        diagram, "mxGraphModel", dx="1200", dy="800", grid="1", gridSize="10",
        guides="1", tooltips="1", connect="1", arrows="1", fold="1",
        page="1", pageScale="1", pageWidth="1600", pageHeight="1200", math="0", shadow="0",
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    # Organization/Folder/Project bounding boxes, drawn before their child
    # nodes so the diagram's z-order puts icons on top of the boxes.
    for box in containers:
        style = (
            "rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;align=left;"
            "spacingLeft=8;spacingTop=6;fontSize=12;fontStyle=1;"
            f"fillColor={box['fill']};strokeColor={box['stroke']};"
        )
        cell = ET.SubElement(root, "mxCell", id=box["id"], value=box["title"],
                              style=style, vertex="1", parent=box["parent"])
        ET.SubElement(cell, "mxGeometry", attrib={
            "x": str(box["x"]), "y": str(box["y"]),
            "width": str(box["w"]), "height": str(box["h"]), "as": "geometry",
        })

    for meta in node_meta.values():
        # Same style draw.io's own built-in GCP icon shapes use: an image shape
        # with the label rendered below the icon rather than a colored box.
        style = (
            "sketch=0;html=1;shape=image;aspect=fixed;imageAspect=0;"
            "verticalLabelPosition=bottom;verticalAlign=top;align=center;"
            "whiteSpace=wrap;fontSize=10;fontColor=#5F6368;labelBackgroundColor=#FFFFFF;"
            f"image=data:image/svg+xml,{meta['icon_image']};"
        )
        cell = ET.SubElement(root, "mxCell", id=meta["id"], value=meta["label"],
                              style=style, vertex="1", parent=meta["parent"])
        ET.SubElement(cell, "mxGeometry", attrib={
            "x": str(meta["x"]), "y": str(meta["y"]),
            "width": str(meta["w"]), "height": str(meta["h"]), "as": "geometry",
        })

    for i, (source, target, label) in enumerate(edges):
        source_id = node_meta[source]["id"]
        target_id = node_meta[target]["id"]
        style = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;"
        edge = ET.SubElement(root, "mxCell", id=f"edge{i}", value=label or "",
                              style=style, edge="1", parent="1", source=source_id, target=target_id)
        ET.SubElement(edge, "mxGeometry", relative="1", attrib={"as": "geometry"})

    return mxfile


def write_drawio(mxfile: ET.Element, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(mxfile, space="  ")
    ET.ElementTree(mxfile).write(output_path, encoding="unicode", xml_declaration=False)
