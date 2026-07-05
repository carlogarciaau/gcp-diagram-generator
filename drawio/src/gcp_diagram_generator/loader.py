"""Loading of Cloud Asset Inventory JSONL snapshot files."""

import json
from pathlib import Path

# Cloud Asset Inventory data can arrive in either camelCase (the default
# `gcloud asset export` JSON output) or snake_case (BigQuery-destination
# exports use snake_case column names, e.g. `asset_type`, `iam_policy`).
# Normalize the specific fields this tool reads so both shapes work without
# touching the rest of the codebase.
_TOP_LEVEL_ALIASES = {
    "asset_type": "assetType",
    "update_time": "updateTime",
    "iam_policy": "iamPolicy",
    "org_policy": "orgPolicy",
    "access_policy": "accessPolicy",
    "access_level": "accessLevel",
    "service_perimeter": "servicePerimeter",
    "os_inventory": "osInventory",
    "related_assets": "relatedAssets",
}
_RESOURCE_ALIASES = {
    "discovery_document_uri": "discoveryDocumentUri",
    "discovery_name": "discoveryName",
    "resource_url": "resourceUrl",
}
_RESOURCE_DATA_ALIASES = {"display_name": "displayName", "project_id": "projectId"}
_OS_INVENTORY_ALIASES = {"os_info": "osInfo"}
_OS_INFO_ALIASES = {"short_name": "shortName", "kernel_version": "kernelVersion"}
_RELATED_ASSETS_BUCKET_ALIASES = {"related_assets": "relatedAssets"}


def _rename_keys(obj: dict, aliases: dict[str, str]) -> None:
    for old_key, new_key in aliases.items():
        if old_key in obj and new_key not in obj:
            obj[new_key] = obj.pop(old_key)


def _normalize_asset(asset: dict) -> dict:
    _rename_keys(asset, _TOP_LEVEL_ALIASES)

    resource = asset.get("resource")
    if isinstance(resource, dict):
        _rename_keys(resource, _RESOURCE_ALIASES)
        data = resource.get("data")
        if isinstance(data, dict):
            _rename_keys(data, _RESOURCE_DATA_ALIASES)

    os_inventory = asset.get("osInventory")
    if isinstance(os_inventory, dict):
        _rename_keys(os_inventory, _OS_INVENTORY_ALIASES)
        os_info = os_inventory.get("osInfo")
        if isinstance(os_info, dict):
            _rename_keys(os_info, _OS_INFO_ALIASES)

    related_assets = asset.get("relatedAssets")
    if isinstance(related_assets, dict):
        relationships = related_assets.get("relationships")
        if isinstance(relationships, dict):
            for bucket in relationships.values():
                if isinstance(bucket, dict):
                    _rename_keys(bucket, _RELATED_ASSETS_BUCKET_ALIASES)

    return asset


def load_jsonl(path: Path) -> list[dict]:
    """Read a newline-delimited JSON asset snapshot file.

    Returns an empty list if the file does not exist, since not every
    content type is required to generate a diagram. Each parsed asset is
    normalized to camelCase field names (see _normalize_asset) to accept
    both `gcloud asset export` and BigQuery-destination snake_case exports.
    """
    if not path.exists():
        return []
    with path.open() as f:
        return [_normalize_asset(json.loads(line)) for line in f if line.strip()]
