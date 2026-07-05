"""Mapping of Cloud Asset Inventory assetType prefixes to `diagrams.gcp` icon classes."""

from diagrams.gcp.analytics import BigQuery, Composer, Dataflow, Dataproc, PubSub
from diagrams.gcp.compute import GKE, AppEngine, ComputeEngine, Functions, Run
from diagrams.gcp.database import SQL, Bigtable, Firestore, Memorystore, Spanner
from diagrams.gcp.devtools import Scheduler, Tasks
from diagrams.gcp.management import Project
from diagrams.gcp.network import (
    DNS,
    Armor,
    ExternalIpAddresses,
    FirewallRules,
    LoadBalancing,
    Network,
    Router,
    VPN,
    VPC,
)
from diagrams.gcp.operations import Logging, Monitoring
from diagrams.gcp.security import (
    AccessContextManager,
    CertificateManager,
    Iam,
    KeyManagementService,
    SecretManager,
)
from diagrams.gcp.storage import GCS, Filestore, PersistentDisk

# (assetType prefix, category label, icon class) - first match wins, more specific
# prefixes listed before their broader parent prefix.
ICON_MAP = [
    ("cloudresourcemanager.googleapis.com/", "Resource Hierarchy", Project),
    ("compute.googleapis.com/Network", "Networking", VPC),
    ("compute.googleapis.com/Subnetwork", "Networking", Network),
    ("compute.googleapis.com/Firewall", "Networking", FirewallRules),
    ("compute.googleapis.com/Router", "Networking", Router),
    ("compute.googleapis.com/Vpn", "Networking", VPN),
    ("compute.googleapis.com/GlobalAddress", "Networking", ExternalIpAddresses),
    ("compute.googleapis.com/Address", "Networking", ExternalIpAddresses),
    ("dns.googleapis.com/", "Networking", DNS),
    ("compute.googleapis.com/BackendService", "Load Balancing", LoadBalancing),
    ("compute.googleapis.com/UrlMap", "Load Balancing", LoadBalancing),
    ("compute.googleapis.com/TargetHttps", "Load Balancing", LoadBalancing),
    ("compute.googleapis.com/SslCertificate", "Load Balancing", CertificateManager),
    ("compute.googleapis.com/HealthCheck", "Load Balancing", LoadBalancing),
    ("compute.googleapis.com/GlobalForwardingRule", "Load Balancing", LoadBalancing),
    ("compute.googleapis.com/SecurityPolicy", "Load Balancing", Armor),
    ("compute.googleapis.com/Disk", "Compute", PersistentDisk),
    ("compute.googleapis.com/Snapshot", "Compute", PersistentDisk),
    ("compute.googleapis.com/", "Compute", ComputeEngine),
    ("container.googleapis.com/", "Containers", GKE),
    ("run.googleapis.com/", "Serverless", Run),
    ("cloudfunctions.googleapis.com/", "Serverless", Functions),
    ("appengine.googleapis.com/", "Serverless", AppEngine),
    ("sqladmin.googleapis.com/", "Storage & Databases", SQL),
    ("redis.googleapis.com/", "Storage & Databases", Memorystore),
    ("spanner.googleapis.com/", "Storage & Databases", Spanner),
    ("bigtableadmin.googleapis.com/", "Storage & Databases", Bigtable),
    ("file.googleapis.com/", "Storage & Databases", Filestore),
    ("firestore.googleapis.com/", "Storage & Databases", Firestore),
    ("storage.googleapis.com/", "Storage & Databases", GCS),
    ("bigquery.googleapis.com/", "Data & Analytics", BigQuery),
    ("dataflow.googleapis.com/", "Data & Analytics", Dataflow),
    ("dataproc.googleapis.com/", "Data & Analytics", Dataproc),
    ("composer.googleapis.com/", "Data & Analytics", Composer),
    ("pubsub.googleapis.com/", "Messaging", PubSub),
    ("cloudtasks.googleapis.com/", "Messaging", Tasks),
    ("cloudscheduler.googleapis.com/", "Messaging", Scheduler),
    ("iam.googleapis.com/", "Security & IAM", Iam),
    ("cloudkms.googleapis.com/", "Security & IAM", KeyManagementService),
    ("secretmanager.googleapis.com/", "Security & IAM", SecretManager),
    ("accesscontextmanager.googleapis.com/", "Security & IAM", AccessContextManager),
    ("logging.googleapis.com/", "Operations", Logging),
    ("monitoring.googleapis.com/", "Operations", Monitoring),
]
DEFAULT_ICON = ("Other", ComputeEngine)

CATEGORY_ORDER = [
    "Resource Hierarchy", "Networking", "Load Balancing", "Compute", "Containers",
    "Serverless", "Storage & Databases", "Data & Analytics", "Messaging",
    "Security & IAM", "Operations", "Other",
]


def categorize(asset_type: str):
    """Return (category_label, icon_class) for an assetType."""
    for prefix, label, icon_class in ICON_MAP:
        if asset_type.startswith(prefix):
            return label, icon_class
    return DEFAULT_ICON
