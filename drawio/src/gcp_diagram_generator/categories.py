"""Mapping of Cloud Asset Inventory assetType prefixes to diagram categories and icons."""

# (assetType prefix, category label, fill color, stroke color, GCP_ICONS key) - first match wins.
CATEGORIES = [
    ("cloudresourcemanager.googleapis.com/", "Resource Hierarchy", "#F5F5F5", "#666666", "Cloud Resource Manager"),
    ("compute.googleapis.com/Network", "Networking", "#DAE8FC", "#6C8EBF", "Virtual Private Cloud"),
    ("compute.googleapis.com/Subnetwork", "Networking", "#DAE8FC", "#6C8EBF", "Cloud Network"),
    ("compute.googleapis.com/Firewall", "Networking", "#DAE8FC", "#6C8EBF", "Cloud Firewall Rules"),
    ("compute.googleapis.com/Router", "Networking", "#DAE8FC", "#6C8EBF", "Cloud Router"),
    ("compute.googleapis.com/Vpn", "Networking", "#DAE8FC", "#6C8EBF", "Cloud VPN"),
    ("compute.googleapis.com/GlobalAddress", "Networking", "#DAE8FC", "#6C8EBF", "Cloud External IP Addresses"),
    ("compute.googleapis.com/Address", "Networking", "#DAE8FC", "#6C8EBF", "Cloud External IP Addresses"),
    ("dns.googleapis.com/", "Networking", "#DAE8FC", "#6C8EBF", "Cloud DNS"),
    ("compute.googleapis.com/BackendService", "Load Balancing", "#D5E8D4", "#82B366", "Cloud Load Balancing"),
    ("compute.googleapis.com/UrlMap", "Load Balancing", "#D5E8D4", "#82B366", "Cloud Load Balancing"),
    ("compute.googleapis.com/TargetHttps", "Load Balancing", "#D5E8D4", "#82B366", "Cloud Load Balancing"),
    ("compute.googleapis.com/SslCertificate", "Load Balancing", "#D5E8D4", "#82B366", "Cloud Load Balancing"),
    ("compute.googleapis.com/HealthCheck", "Load Balancing", "#D5E8D4", "#82B366", "Cloud Load Balancing"),
    ("compute.googleapis.com/GlobalForwardingRule", "Load Balancing", "#D5E8D4", "#82B366", "Cloud Load Balancing"),
    ("compute.googleapis.com/SecurityPolicy", "Load Balancing", "#D5E8D4", "#82B366", "Cloud Armor"),
    ("compute.googleapis.com/Disk", "Compute", "#FFE6CC", "#D79B00", "Persistent Disk"),
    ("compute.googleapis.com/Snapshot", "Compute", "#FFE6CC", "#D79B00", "Persistent Disk"),
    ("compute.googleapis.com/", "Compute", "#FFE6CC", "#D79B00", "Compute Engine"),
    ("container.googleapis.com/", "Containers", "#FFE6CC", "#D79B00", "Google Kubernetes Engine"),
    ("run.googleapis.com/", "Serverless", "#FFF2CC", "#D6B656", "Cloud Run"),
    ("cloudfunctions.googleapis.com/", "Serverless", "#FFF2CC", "#D6B656", "Cloud Functions"),
    ("appengine.googleapis.com/", "Serverless", "#FFF2CC", "#D6B656", "App Engine"),
    ("sqladmin.googleapis.com/", "Storage & Databases", "#E1D5E7", "#9673A6", "Cloud SQL"),
    ("redis.googleapis.com/", "Storage & Databases", "#E1D5E7", "#9673A6", "Memorystore"),
    ("spanner.googleapis.com/", "Storage & Databases", "#E1D5E7", "#9673A6", "Cloud Spanner"),
    ("bigtableadmin.googleapis.com/", "Storage & Databases", "#E1D5E7", "#9673A6", "Cloud Bigtable"),
    ("file.googleapis.com/", "Storage & Databases", "#E1D5E7", "#9673A6", "Filestore"),
    ("firestore.googleapis.com/", "Storage & Databases", "#E1D5E7", "#9673A6", "Firestore"),
    ("storage.googleapis.com/", "Storage & Databases", "#E1D5E7", "#9673A6", "Cloud Storage"),
    ("bigquery.googleapis.com/", "Data & Analytics", "#F8CECC", "#B85450", "BigQuery"),
    ("dataflow.googleapis.com/", "Data & Analytics", "#F8CECC", "#B85450", "Dataflow"),
    ("dataproc.googleapis.com/", "Data & Analytics", "#F8CECC", "#B85450", "Dataproc"),
    ("composer.googleapis.com/", "Data & Analytics", "#F8CECC", "#B85450", "Cloud Composer"),
    ("pubsub.googleapis.com/", "Messaging", "#D5E8D4", "#82B366", "Pub/Sub"),
    ("cloudtasks.googleapis.com/", "Messaging", "#D5E8D4", "#82B366", "Cloud Tasks"),
    ("cloudscheduler.googleapis.com/", "Messaging", "#D5E8D4", "#82B366", "Cloud Scheduler"),
    ("iam.googleapis.com/", "Security & IAM", "#F8CECC", "#B85450", "Cloud IAM"),
    ("cloudkms.googleapis.com/", "Security & IAM", "#F8CECC", "#B85450", "Cloud Key Management"),
    ("secretmanager.googleapis.com/", "Security & IAM", "#F8CECC", "#B85450", "Secret Manager"),
    ("accesscontextmanager.googleapis.com/", "Security & IAM", "#F8CECC", "#B85450", "Security Command Center"),
    ("logging.googleapis.com/", "Operations", "#F5F5F5", "#666666", "Cloud Logging"),
    ("monitoring.googleapis.com/", "Operations", "#F5F5F5", "#666666", "Cloud Monitoring"),
]
DEFAULT_CATEGORY = ("Other", "#FFFFFF", "#000000", "Cloud APIs")

COLUMN_ORDER = [
    "Resource Hierarchy", "Networking", "Load Balancing", "Compute", "Containers",
    "Serverless", "Storage & Databases", "Data & Analytics", "Messaging",
    "Security & IAM", "Operations", "Other",
]


def categorize(asset_type: str) -> tuple[str, str, str, str]:
    """Return (category_label, fill_color, stroke_color, icon_label) for an assetType.

    icon_label is a key into gcp_icons.GCP_ICONS.
    """
    for prefix, label, fill, stroke, icon_label in CATEGORIES:
        if asset_type.startswith(prefix):
            return label, fill, stroke, icon_label
    return DEFAULT_CATEGORY
