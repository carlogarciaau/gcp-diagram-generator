"""Build a node/edge/container graph model from selected Cloud Asset Inventory content types.

Nodes are grouped into nested clusters that mirror the resource hierarchy: an
Organization-level cluster, one Folder cluster per folder (each containing
one Project cluster per project it holds), so the diagram shows the bounded
context each resource belongs to.
"""

from .icon_map import categorize

HIERARCHY_TYPES = {
    "cloudresourcemanager.googleapis.com/Organization",
    "cloudresourcemanager.googleapis.com/Folder",
    "cloudresourcemanager.googleapis.com/Project",
}

# Content types that contribute nodes to the diagram. RESOURCE assets always
# have a `resource` field; ACCESS_POLICY assets (AccessPolicy/AccessLevel/
# ServicePerimeter) instead have accessPolicy/accessLevel/servicePerimeter
# fields and don't appear under the RESOURCE content type in a real export.
NODE_PRODUCING_CONTENT_TYPES = ("resource", "access-policy")

CONTENT_TYPE_CHOICES = (
    "resource", "relationship", "iam-policy", "org-policy", "access-policy", "os-inventory",
)


def short_label(asset: dict) -> str:
    name = asset["name"]
    resource_id = name.rstrip("/").split("/")[-1]
    kind = asset["assetType"].split("/")[-1]
    # Organization/Folder/Project resource names are just numeric IDs; prefer
    # their human-readable displayName/projectId when available.
    data = asset.get("resource", {}).get("data", {})
    friendly_name = data.get("displayName") or data.get("projectId")
    display_id = friendly_name if friendly_name else resource_id
    return f"{display_id}\n({kind})"


def _display_title(asset: dict) -> str:
    data = asset.get("resource", {}).get("data", {})
    friendly_name = data.get("displayName") or data.get("projectId")
    display_id = friendly_name if friendly_name else asset["name"].rstrip("/").split("/")[-1]
    kind = asset["assetType"].split("/")[-1]
    return f"{display_id} ({kind})"


def _parent_from_nested_name(name: str) -> str | None:
    """Derive a parent asset name from ACCESS_POLICY-style nested resource names.

    e.g. accessPolicies/123/accessLevels/foo -> accessPolicies/123
    """
    parts = name.rstrip("/").rsplit("/", 2)
    return parts[0] if len(parts) == 3 else None


def _resolve_short_reference(short_ref: str, assets_by_name: dict) -> str | None:
    """Match a short resource reference (e.g. "projects/123") to a full asset name."""
    for name in assets_by_name:
        if name == short_ref or name.endswith("/" + short_ref):
            return name
    return None


def _build_box_tree(node_source_assets: list[dict]) -> dict:
    """Group node-producing assets into an Organization > Folder > Project box tree.

    Each box is {"title", "resources": [asset names], "children": [box, ...]}.
    "resources" always includes the org/folder/project's own asset name first
    (if present) so its IAM/OrgPolicy annotations still render as a node.
    """
    folder_assets = {a["ancestors"][0]: a for a in node_source_assets
                      if a["assetType"] == "cloudresourcemanager.googleapis.com/Folder"}
    project_assets = {a["ancestors"][0]: a for a in node_source_assets
                       if a["assetType"] == "cloudresourcemanager.googleapis.com/Project"}
    org_asset = next((a for a in node_source_assets
                       if a["assetType"] == "cloudresourcemanager.googleapis.com/Organization"), None)

    folder_to_project_resources: dict[str, dict[str, list[str]]] = {ref: {} for ref in folder_assets}
    folder_loose_resources: dict[str, list[str]] = {ref: [] for ref in folder_assets}
    org_loose_resources: list[str] = []

    for asset in node_source_assets:
        if asset["assetType"] in HIERARCHY_TYPES:
            continue
        ancestors = asset.get("ancestors", [])
        project_ref = next((a for a in ancestors if a.startswith("projects/")), None)
        folder_ref = next((a for a in ancestors if a.startswith("folders/")), None)

        if project_ref in project_assets:
            if folder_ref in folder_assets:
                folder_to_project_resources[folder_ref].setdefault(project_ref, []).append(asset["name"])
            else:
                # A project with no matching folder in this dataset (unusual) -
                # surface it at the org level rather than dropping it silently.
                org_loose_resources.append(asset["name"])
        elif folder_ref in folder_assets:
            folder_loose_resources[folder_ref].append(asset["name"])
        else:
            org_loose_resources.append(asset["name"])

    folder_boxes = []
    for folder_ref, folder_asset in folder_assets.items():
        project_boxes = []
        for project_ref, resource_names in folder_to_project_resources[folder_ref].items():
            project_asset = project_assets[project_ref]
            project_boxes.append({
                "title": _display_title(project_asset),
                "resources": [project_asset["name"]] + resource_names,
                "children": [],
            })
        folder_boxes.append({
            "title": _display_title(folder_asset),
            "resources": [folder_asset["name"]] + folder_loose_resources[folder_ref],
            "children": project_boxes,
        })

    org_resources = ([org_asset["name"]] if org_asset else []) + org_loose_resources
    org_box = {
        "title": _display_title(org_asset) if org_asset else "Organization",
        "resources": org_resources,
        "children": [],
    }

    return {"org_box": org_box, "folder_boxes": folder_boxes}


def build_diagram(content_data: dict[str, list[dict]]):
    """Return (node_meta, edges, box_tree) built from the selected content types.

    content_data maps content-type name (see CONTENT_TYPE_CHOICES) to the list
    of assets loaded for it; a content type absent from the dict is treated as
    not selected. Only 'resource' and 'access-policy' assets become nodes;
    'relationship' becomes edges; 'iam-policy'/'org-policy'/'os-inventory'
    annotate the label of whichever existing node shares their asset name.

    node_meta maps asset name -> dict(label, icon_class).
    edges is a list of (source_name, target_name, label) tuples.
    box_tree is {"org_box": box, "folder_boxes": [box, ...]} describing the
    Organization/Folder/Project nesting, where each box is
    {"title", "resources": [asset names], "children": [box, ...]}.
    """
    resources = content_data.get("resource", [])
    access_policies = content_data.get("access-policy", [])
    relationships = content_data.get("relationship", [])

    node_source_assets = list(resources) + list(access_policies)
    if not node_source_assets:
        raise ValueError(
            "No selected content type produces diagram nodes; include 'resource' and/or "
            "'access-policy' in --content-types."
        )

    assets_by_name = {a["name"]: a for a in node_source_assets}

    node_meta: dict[str, dict] = {}
    for asset in node_source_assets:
        _, icon_class = categorize(asset["assetType"])
        node_meta[asset["name"]] = {
            "label": short_label(asset),
            "icon_class": icon_class,
        }

    box_tree = _build_box_tree(node_source_assets)

    edges: list[tuple[str, str, str | None]] = []

    # Containment edges: parent -> child, skip cloudresourcemanager parents
    # (Project/Folder/Org) unless the child is itself part of that hierarchy,
    # so the diagram isn't dominated by a star topology around the project.
    for asset in resources:
        parent = asset.get("resource", {}).get("parent")
        if not parent or parent not in assets_by_name:
            continue
        parent_asset = assets_by_name[parent]
        is_hierarchy_parent = parent_asset["assetType"].startswith("cloudresourcemanager.googleapis.com/")
        is_hierarchy_child = asset["assetType"].startswith("cloudresourcemanager.googleapis.com/")
        if is_hierarchy_parent and not is_hierarchy_child:
            continue
        edges.append((parent, asset["name"], None))

    # ACCESS_POLICY containment: AccessPolicy -> AccessLevel/ServicePerimeter,
    # derived from name nesting since these assets have no `resource.parent`.
    for asset in access_policies:
        parent = _parent_from_nested_name(asset["name"])
        if parent and parent in assets_by_name:
            edges.append((parent, asset["name"], None))

    # ServicePerimeter -> protected resource edges.
    for asset in access_policies:
        perimeter = asset.get("servicePerimeter")
        if not perimeter:
            continue
        for short_ref in perimeter.get("status", {}).get("resources", []):
            target = _resolve_short_reference(short_ref, assets_by_name)
            if target:
                edges.append((asset["name"], target, "PROTECTS"))

    # Functional edges from the RELATIONSHIP content type.
    for rel_asset in relationships:
        source = rel_asset["name"]
        rel_map = rel_asset.get("relatedAssets", {}).get("relationships", {})
        for rel_type, bucket in rel_map.items():
            for related in bucket.get("relatedAssets", []):
                target = related["asset"]
                if source in node_meta and target in node_meta:
                    edges.append((source, target, rel_type))

    # Label annotations from enrichment content types - only applied to nodes
    # that already exist (i.e. also present under a node-producing type).
    for asset in content_data.get("iam-policy", []):
        node = node_meta.get(asset["name"])
        if node:
            bindings = asset.get("iamPolicy", {}).get("bindings", [])
            node["label"] += f"\nIAM: {len(bindings)} binding(s)"

    for asset in content_data.get("org-policy", []):
        node = node_meta.get(asset["name"])
        if node:
            constraints = asset.get("orgPolicy", [])
            node["label"] += f"\nOrgPolicy: {len(constraints)} constraint(s)"

    for asset in content_data.get("os-inventory", []):
        node = node_meta.get(asset["name"])
        if node:
            os_info = asset.get("osInventory", {}).get("osInfo", {})
            if os_info:
                node["label"] += f"\nOS: {os_info.get('shortName', '?')} {os_info.get('version', '')}"

    return node_meta, edges, box_tree
