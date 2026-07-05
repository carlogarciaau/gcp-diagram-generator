import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gcp_diagram_generator_graphviz.graph import build_diagram
from gcp_diagram_generator_graphviz.loader import load_jsonl
from gcp_diagram_generator_graphviz.render import render_diagram

MOCK_DATA_DIR = Path(__file__).parent.parent.parent / "mock-data" / "asset-inventory"


def load_content(*content_types: str) -> dict:
    return {ct: load_jsonl(MOCK_DATA_DIR / f"{ct}.json") for ct in content_types}


def _all_resource_names(box: dict) -> set[str]:
    names = set(box["resources"])
    for child in box["children"]:
        names |= _all_resource_names(child)
    return names


class TestGenerateDiagram(unittest.TestCase):
    def setUp(self):
        self.resources = load_jsonl(MOCK_DATA_DIR / "resource.json")
        self.relationships = load_jsonl(MOCK_DATA_DIR / "relationship.json")

    def test_mock_resources_load(self):
        self.assertGreater(len(self.resources), 0)

    def test_build_diagram_produces_a_node_per_resource(self):
        node_meta, edges, box_tree = build_diagram(load_content("resource", "relationship"))
        self.assertEqual(len(node_meta), len(self.resources))
        self.assertGreater(len(edges), 0)

    def test_every_edge_endpoint_exists_as_a_node(self):
        node_meta, edges, box_tree = build_diagram(load_content("resource", "relationship"))
        for source, target, _ in edges:
            self.assertIn(source, node_meta)
            self.assertIn(target, node_meta)

    def test_resource_only_omits_relationship_edges(self):
        node_meta, edges, box_tree = build_diagram(load_content("resource"))
        self.assertEqual(len(node_meta), len(self.resources))
        self.assertTrue(all(label is None for _, _, label in edges))

    def test_access_policy_adds_nodes_and_containment_edges(self):
        node_meta, edges, box_tree = build_diagram(load_content("resource", "access-policy"))
        access_policy_assets = load_jsonl(MOCK_DATA_DIR / "access-policy.json")
        self.assertEqual(len(node_meta), len(self.resources) + len(access_policy_assets))
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

    def test_box_tree_covers_every_node(self):
        node_meta, edges, box_tree = build_diagram(load_content("resource", "access-policy"))
        boxed_names = _all_resource_names(box_tree["org_box"])
        for folder_box in box_tree["folder_boxes"]:
            boxed_names |= _all_resource_names(folder_box)
        self.assertEqual(boxed_names, set(node_meta.keys()))

    def test_box_tree_nests_org_folder_project(self):
        node_meta, edges, box_tree = build_diagram(load_content("resource"))
        self.assertTrue(box_tree["org_box"]["title"].endswith("(Organization)"))
        self.assertEqual(len(box_tree["folder_boxes"]), 3)
        for folder_box in box_tree["folder_boxes"]:
            self.assertTrue(folder_box["title"].endswith("(Folder)"))
            self.assertEqual(len(folder_box["children"]), 1)
            self.assertTrue(folder_box["children"][0]["title"].endswith("(Project)"))

    def test_render_writes_an_image_file(self):
        node_meta, edges, box_tree = build_diagram(load_content("resource", "relationship"))
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "diagram"
            render_diagram(node_meta, edges, box_tree, output_path, output_format="png")
            self.assertTrue(output_path.with_suffix(".png").exists())


if __name__ == "__main__":
    unittest.main()
