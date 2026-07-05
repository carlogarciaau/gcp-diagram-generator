import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from gcp_diagram_generator.drawio import render_mxgraph
from gcp_diagram_generator.graph import build_diagram
from gcp_diagram_generator.loader import load_jsonl

MOCK_DATA_DIR = Path(__file__).parent.parent.parent / "mock-data" / "asset-inventory"


def load_content(*content_types: str) -> dict:
    return {ct: load_jsonl(MOCK_DATA_DIR / f"{ct}.json") for ct in content_types}


class TestGenerateDiagram(unittest.TestCase):
    def setUp(self):
        self.resources = load_jsonl(MOCK_DATA_DIR / "resource.json")
        self.relationships = load_jsonl(MOCK_DATA_DIR / "relationship.json")

    def test_mock_resources_load(self):
        self.assertGreater(len(self.resources), 0)

    def test_build_diagram_produces_a_node_per_resource(self):
        node_meta, edges, containers = build_diagram(load_content("resource", "relationship"))
        self.assertEqual(len(node_meta), len(self.resources))
        self.assertGreater(len(edges), 0)

    def test_rendered_output_is_valid_xml(self):
        node_meta, edges, containers = build_diagram(load_content("resource", "relationship"))
        mxfile = render_mxgraph(node_meta, edges, containers)
        xml_string = ET.tostring(mxfile, encoding="unicode")
        # Round-trips through the parser without raising.
        ET.fromstring(xml_string)

    def test_every_edge_endpoint_exists_as_a_node(self):
        node_meta, edges, containers = build_diagram(load_content("resource", "relationship"))
        for source, target, _ in edges:
            self.assertIn(source, node_meta)
            self.assertIn(target, node_meta)

    def test_resource_only_omits_relationship_edges(self):
        # Containment edges (derived from resource.parent) still appear, but
        # RELATIONSHIP-sourced edges (which always carry a label) should not.
        node_meta, edges, containers = build_diagram(load_content("resource"))
        self.assertEqual(len(node_meta), len(self.resources))
        self.assertTrue(all(label is None for _, _, label in edges))

    def test_access_policy_adds_nodes_and_containment_edges(self):
        node_meta, edges, containers = build_diagram(load_content("resource", "access-policy"))
        access_policy_assets = load_jsonl(MOCK_DATA_DIR / "access-policy.json")
        self.assertEqual(len(node_meta), len(self.resources) + len(access_policy_assets))
        # AccessPolicy -> AccessLevel/ServicePerimeter containment edges exist.
        access_policy_edges = [e for e in edges if "accessPolicies" in e[0] and "accessPolicies" in e[1]]
        self.assertGreater(len(access_policy_edges), 0)

    def test_iam_policy_annotates_existing_node_label(self):
        base_node_meta, _, _ = build_diagram(load_content("resource"))
        annotated_node_meta, _, _ = build_diagram(load_content("resource", "iam-policy"))
        project_name = "//cloudresourcemanager.googleapis.com/projects/345678901234"
        self.assertNotIn("IAM:", base_node_meta[project_name]["label"])
        self.assertIn("IAM:", annotated_node_meta[project_name]["label"])

    def test_no_node_producing_content_type_raises(self):
        with self.assertRaises(ValueError):
            build_diagram(load_content("iam-policy", "relationship"))

    def test_every_node_parent_is_a_container_or_root(self):
        node_meta, edges, containers = build_diagram(load_content("resource", "access-policy"))
        container_ids = {c["id"] for c in containers}
        for meta in node_meta.values():
            self.assertIn(meta["parent"], container_ids)

    def test_containers_nest_org_folder_project(self):
        node_meta, edges, containers = build_diagram(load_content("resource"))
        by_kind = {}
        for c in containers:
            by_kind.setdefault(c.get("fill"), []).append(c)
        org_boxes = [c for c in containers if c["parent"] == "1" and c["title"].endswith("(Organization)")]
        folder_boxes = [c for c in containers if c["parent"] == "1" and c["title"].endswith("(Folder)")]
        self.assertEqual(len(org_boxes), 1)
        self.assertEqual(len(folder_boxes), 3)
        folder_ids = {c["id"] for c in folder_boxes}
        project_boxes = [c for c in containers if c["title"].endswith("(Project)")]
        self.assertEqual(len(project_boxes), 3)
        self.assertTrue(all(p["parent"] in folder_ids for p in project_boxes))


if __name__ == "__main__":
    unittest.main()
