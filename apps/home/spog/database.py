import datetime

import sqlalchemy as db
from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import create_database, database_exists
from flask_login import UserMixin

Base = declarative_base()

def azure_cli_creds(KeyVaultName, secretName):
    credential = AzureCliCredential()
    KVUri = "https://{}.vault.azure.net".format(KeyVaultName)
    client = SecretClient(vault_url=KVUri, credential=credential)
    retrieved_secret = client.get_secret(secretName)
    return retrieved_secret.value


def postgresbind():
    postgres = azure_cli_creds("kclkeyrpsecretdevneu1", "SPOGWazeODBC")
    engine = create_engine(postgres, echo=True)
    return engine


def deploy_database():
    postgres = azure_cli_creds("kclkeyrpsecretdevneu1", "SPOGWazeODBC")
    engine = create_engine(postgres, echo=True)
    if not database_exists(engine.url):
        create_database(engine.url)
        Base.metadata.create_all(engine)

class User(UserMixin,Base):
    __tablename__ = "kcl_users"    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(128))
    name = db.Column(db.String(64))

class kingsCollegeLondonRCSApplications(Base):
    __tablename__ = "kcl_applications"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    name = Column("name", String)
    contact = Column("contact", String)
    description = Column("description", String)
    note = Column("note", String)
    resourcegroup = Column("resource_group", String)
    uuid = Column("uuid", String)
    azureinventory = Column("azure_inventory", String)
    cloudabilityviewid = Column("cloudability_view_id", Integer)
    platform = Column("platform", String)

    def obj_to_dict(self):
        """Return object data in serializeable format"""
        return {
            'id': self.id,
            'created_date': self.created_date,
            'name': self.name,
            'contact': self.contact,
            'description': self.description,
            'note': self.note,
            'resourcegroup': self.resourcegroup,
            'uuid': self.uuid,
            'azureinventory': self.azureinventory,
            'cloudabilityviewid': self.cloudabilityviewid,
            'platform': self.platform
        }


class KingsCollegeLondonResourceGroups(Base):
    __tablename__ = "kcl_resource_groups"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    applicationName = Column("application", String)
    resourceGroup = Column("resource_group", String)


class azureWebApps(Base):
    __tablename__ = "azure_webapps"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    date = Column("date_ingested", db.Date)
    name = Column("name", String)
    type = Column("type", String)
    kind = Column("kind", String)
    location = Column("location", String)
    environment = Column("environment", String)
    application = Column("application", String)
    tier = Column("tier", Integer)
    firewall = Column("Firewall", String)
    department = Column("department", String)
    costcentre = Column("costcentre", Integer)
    state = Column("state", String)
    hostnames = Column("hostnames", ARRAY(String))
    usagestate = Column("usage_state", String)
    computemode = Column("compute_mode", String)
    storagerecoverydefaultstate = Column("storageRecoveryDefaultState", String)
    deploymentid = Column("deployment_id", String)
    sku = Column("sku", String)
    inboundipaddress = Column("inbound_ip_address", String)
    resourcegroup = Column("resource_group", String)


class azureDefenderAlerts(Base):
    __tablename__ = "azure_defender_alerts"
    id = Column("id", Integer, primary_key=True)
    azure_id = Column("azure_id", String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    productname = Column("Productname", String)
    type = Column("type", String)
    ipaddress = Column("ipaddress", String)
    compromisedentity = Column("compromisedentity", String)
    killchainintent = Column("killchainintent", String)
    description = Column("description", String)
    remeditationsteps = Column("remediationsteps", String)
    severity = Column("severity", String)

class azureDefenderAlertsByResourceGroup(Base):
    __tablename__ = "azure_defender_alerts_by_resource_group"
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    id = Column("id", Integer, primary_key=True)
    systemName = Column("system_name", String)
    uuid = Column("uuid", String)


class ASCScore(Base):
    __tablename__ = "azure_asc_score"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    date = Column("date_ingested", db.Date)
    current = Column("current", Integer)


class SecureScoreControls(Base):
    __tablename__ = "azure_secure_score_controls"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    date = Column("date_ingested", db.Date)
    displayname = Column(String)
    healthyresourcesount = Column("healthyResourceCount", Integer)
    unhealthyresourcecount = Column("unhealthyResourceCount", Integer)
    notapplicableresourcecount = Column("notApplicableResourceCount", Integer)


class DefenderForCloudSettings(Base):
    __tablename__ = "azure_defender_for_cloud_settings"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    date = Column("date_ingested", db.Date)
    name = Column(String)
    kind = Column(String)
    enabled = Column(String)


class azureResourceGroups(Base):
    __tablename__ = "azure_resource_groups"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    azure_id = Column("azure_id", String)
    date = Column("date_ingested", db.Date)
    name = Column("name", String)
    location = Column("location", String)
    type = Column("type", String)
    provisioningstate = Column("provisioningState", String)


class azureResources(Base):
    __tablename__ = "azure_resources"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    azure_id = Column("azure_id", String)
    date = Column("date_ingested", db.Date)
    name = Column("name", String)
    type = Column("type", String)
    location = Column("location", String)
    environment = Column("Environment", String)
    application = Column("Application", String)
    tier = Column("Tier", String)
    department = Column("Department", String)
    costcentre = Column("Cost_Centre", Integer)
    firewall = Column("Firewall", Integer)


class alertsbyResourceGroup(Base):
    __tablename__ = "kcl_alerts_by_resource_group"
    id = Column("id", Integer, primary_key=True)
    resourcegroup = Column("resource_group", String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    name = Column("name", String)
    type = Column("type", String)
    status = Column("status", String)
    alerttype = Column("alertType", String)
    compromisedentity = Column("compromisedEntity", String)
    timegenerated = Column("timeGeneratedUtc", String)
    version = Column("version", String)
    intent = Column("intent", String)
    productname = Column("productName", String)
    productcomponentname = Column("productComponentName", String)
    severity = Column("severity", String)
    alerturi = Column("alertURI", String)
    isinicident = Column("isIncident", String)
    uuid = Column("uuid", String)


class azureOperationalInsightsOperations(Base):
    __tablename__ = "azure_operational_insights"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    date = Column("date_ingested", db.Date)
    name = Column("name", String)
    provider = Column("provider", String)
    resource = Column("resource", String)
    operation = Column("operation", String)
    description = Column("description", String)


class CloudAbilityViews(Base):
    __tablename__ = "cloudability_views"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    vendor = Column("vendor", String)
    cost = Column("cost", db.Float)
    system = Column("system", String)
    resourcegroup = Column("resource_group", String)
    uuid = Column("uuid", String)
    description = Column("description", String)
    daterange = Column("date_range", Integer)

class CloudabilityFinancialYear(Base):
    __tablename__ = "cloudability_financial_year"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    vendor = Column("vendor", String)
    cost = Column("cost", db.Float)
    system = Column("system", String)
    resourcegroup = Column("resource_group", String)
    uuid = Column("uuid", String)
    description = Column("description", String)
    daterange = Column("date_range", Integer)

class CloudAbilityPlatformViews(Base):
    __tablename__ = "cloudability_platform_views"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    vendor = Column("vendor", String)
    platform = Column("platform", String)
    cost = Column("cost", db.Float)
    system = Column("system", String)
    description = Column("description", String)
    daterange = Column("date_range", Integer)


class CloudAbilityInventory(Base):
    __tablename__ = "cloudability_view_inventory"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    title = Column("title", String)
    view = Column("view_id", Integer)


class CloudAbilityScoreCardMetrics(Base):
    __tablename__ = "cloudability_scorecard_metrics"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    overallscore = Column("overall_score", String)
    topcomputespend = Column("top_compute_spend", Integer)
    elasticityscore = Column("elasticityscore", String)
    pricingscore = Column("pricing_score", Integer)
    system = Column("system", String)
    view = Column("view", Integer)
    uuid = Column("uuid", String)
    date = Column("date_ingested", db.Date)


class CloudAbilityForecastDetail(Base):
    __tablename__ = "cloudability_forecasts"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    view = Column("view_id", Integer)
    system = Column("system_name", String)
    uuid = Column("uuid", String)
    forecastServiceMonth = Column("forecast_service_month", String)
    forecastServiceSpend = Column("forecast_service_spend", Integer)
    forecastServiceName = Column("actual_service_name", String)
    forecastUsageFamily = Column("actual_usage_family", String)

class CloudAbilityForecastDetailByPlatform(Base):
    __tablename__ = "cloudability_forecasts_by_platform"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    view = Column("view_id", Integer)
    system = Column("system_name", String)
    uuid = Column("uuid", String)
    forecastServiceMonth = Column("forecast_service_month", String)
    forecastServiceSpend = Column("forecast_service_spend", Integer)
    forecastServiceName = Column("actual_service_name", String)
    forecastUsageFamily = Column("actual_usage_family", String)

class CloudAbilityForecastGeneric(Base):
    __tablename__ = "cloudability_generic_forecast"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    view = Column("view", Integer)
    system = Column("system_name", String)
    uuid = Column("uuid", String)
    month = Column("month", String)
    lowerBound = Column("lower_bound", Integer)
    spend = Column("spend", Integer)
    upperBound = Column("upper_bound", Integer)


class CloudAbilityActualSpend(Base):
    __tablename__ = "cloudability_actual_spend"
    id = Column("id", Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    view = Column("view_id", Integer)
    system = Column("system_name", String)
    uuid = Column("uuid", String)
    month = Column("month", String)
    spend = Column("spend", Integer)

class KingsCollegeLondonResourceInventory(Base):
    __tablename__ = "kcl_resource_inventory"
    id = Column("id", Integer, primary_key=True)
    azure_id = Column("azure_id", String)
    uuid = Column("uuid", String)
    resourcegroup = Column("resource_group", String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow().strftime('%B %d %Y'))
    name = Column("name", String)
    type = Column("type", String)
    managedby = Column("managedby", String)
    location = Column("location", String)
    skuName = Column("sku_name", String)
    skuTier = Column("sku_tier", String)
    sku_family = Column("sku_family", String)
    sku_capacity = Column("skucapacity", Integer)
    environment = Column("environment", String)
    application = Column("application", String)
    tier = Column("tier", Integer)
    department = Column("department", String)
    costcentre = Column("cost_centre", Integer)
    firewall = Column("firewall", Integer)