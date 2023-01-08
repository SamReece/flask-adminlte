import datetime

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.configuration import azure_access_token, get_urls, read_json
from src.database import (
    ASCScore,
    DefenderForCloudSettings,
    SecureScoreControls,
    azure_cli_creds,
    azureDefenderAlerts,
    azureOperationalInsightsOperations,
    azureResourceGroups,
    azureResources,
    azureWebApps,
    postgresbind,
)


class AzureResources(object):
    def __init__(self, url=None):
        self.scope = "MANAGEMENT"
        self.url = url
        self.config = read_json("cfg/configuration.json")
        self.postgres = azure_cli_creds("kclkeyrpsecretdevneu1", "SPOGWazeODBC")
        self.engine = create_engine(self.postgres)
        self.Session = sessionmaker(bind=postgresbind())

    def get_api_request_kcl_azure(self, endpoint):
        config = read_json("cfg/configuration.json")
        scope = config["SCOPES"][self.scope]
        token = azure_access_token(scope)
        endpoint = config["URLS"][endpoint]
        payload = {"Authorization": "bearer " + token}
        request = requests.get(endpoint, headers=payload)
        return request.json()

    def azure_operational_insights(self):
        data = self.get_api_request_kcl_azure("AZURE_INSIGHTS")
        with self.Session() as session:
            for i in data["value"]:
                try:
                    insights = azureOperationalInsightsOperations()
                    insights.date = datetime.datetime.now().date()
                    insights.name = i.get("name", "No Name")
                    insights.provider = i.get("display", {}).get("provider", "No Data")
                    insights.resource = i.get("display", {}).get("resource", "No Data")
                    insights.operation = i.get("display", {}).get(
                        "operation", "No Data"
                    )
                    insights.description = i.get("display", {}).get(
                        "description", "No Data"
                    )
                    session.add(insights)
                    session.commit()
                finally:
                    session.close()

    def azure_resource_groups(self):
        data = self.get_api_request_kcl_azure("AZURE_RESOURCE_GROUPS")
        with self.Session() as session:
            for i in data["value"]:
                try:
                    resourcegroups = azureResourceGroups()
                    resourcegroups.date = datetime.datetime.now().date()
                    resourcegroups.azure_id = i.get("id")
                    resourcegroups.name = i.get("name")
                    resourcegroups.location = i.get("location")
                    resourcegroups.type = i.get("type")
                    resourcegroups.provisioningstate = i.get("properties", {}).get(
                        "provisioningState", "No Data"
                    )
                    session.add(resourcegroups)
                    session.commit()
                finally:
                    session.close()

    def azure_resources(self):
        data = self.get_api_request_kcl_azure("AZURE_RESOURCES")
        with self.Session() as session:
            for i in data["value"]:
                try:
                    resources = azureResources()
                    resources.date = datetime.datetime.now().date()
                    resources.azure_id = i.get("id")
                    resources.name = i.get("name")
                    resources.type = i.get("type")
                    resources.location = i.get("location")
                    resources.environment = i.get("tags", {}).get(
                        "Environment", "No Data"
                    )
                    resources.application = i.get("tags", {}).get(
                        "Application", "No Data"
                    )
                    resources.tier = i.get("tags", {}).get("Tier", "No Data")
                    resources.department = i.get("tags", {}).get(
                        "Department", "No Data"
                    )
                    resources.costcentre = i.get("tags", {}).get("Cost Centre", 0)
                    resources.firewall = i.get("tags", {}).get("Firewall", 0)
                    session.add(resources)
                    session.commit()
                finally:
                    session.close()
                    

    def azure_secure_score(self):
        data = self.get_api_request_kcl_azure("SECURE_SCORE")
        with self.Session() as session:
            for i in data["value"]:
                try:
                    ASCSCORE = ASCScore()
                    ASCSCORE.date = datetime.datetime.now().date()
                    ASCSCORE.current = (
                        i.get("properties", {}).get("score", {}).get("current")
                    )
                    session.add(ASCSCORE)
                    session.commit()
                finally:
                    session.close()
                    

    def azure_secure_score_controls(self):
        data = self.get_api_request_kcl_azure("SECURE_SCORE_CONTROLS")
        with self.Session() as session:
            for i in data["value"]:
                try:
                    ascscorecontrols = SecureScoreControls()
                    ascscorecontrols.date = datetime.datetime.now().date()
                    ascscorecontrols.displayname = i.get("properties", {}).get(
                        "displayName"
                    )
                    ascscorecontrols.healthyresourcesount = i.get("properties", {}).get(
                        "healthyResourceCount"
                    )
                    ascscorecontrols.unhealthyresourcecount = i.get(
                        "properties", {}
                    ).get("unhealthyResourceCount")
                    ascscorecontrols.notapplicableresourcecount = i.get(
                        "properties", {}
                    ).get("notApplicableResourceCount")
                    session.add(ascscorecontrols)
                    session.commit()
                finally:
                    session.close()

    def azure_defender_for_cloud_alerts(self):
        data = self.get_api_request_kcl_azure("DEFENDER_ALERTS")
        with self.Session() as session:
            for i in data["value"]:
                try:
                    defenderAlerts = azureDefenderAlerts()
                    defenderAlerts.azure_id = (
                        i.get("properties", {})
                        .get("resourceIdentifiers", {})[0]
                        .get("azureResourceId", "No Data")
                    )
                    defenderAlerts.productname = i.get("properties", {}).get(
                        "productName", "No Data"
                    )
                    defenderAlerts.type = (
                        i.get("properties", {})
                        .get("resourceIdentifiers", {})[0]
                        .get("type")
                    )
                    defenderAlerts.ipaddress = (
                        i.get("properties", {}).get("entities", {})[1].get("address", 0)
                    )
                    defenderAlerts.compromisedentity = i.get("properties", {}).get(
                        "compromisedEntity", "No Data"
                    )
                    defenderAlerts.killchainintent = i.get("properties", {}).get(
                        "intent", "No Data"
                    )
                    defenderAlerts.description = i.get("properties", {}).get(
                        "description", "No Data"
                    )
                    defenderAlerts.remeditationsteps = i.get("properties", {}).get(
                        "remediationSteps", "No Data"
                    )
                    defenderAlerts.severity = i.get("properties", {}).get(
                        "severity", "No Data"
                    )
                    session.add(defenderAlerts)
                    session.commit()
                finally:
                    session.close()

    def azure_defender_for_cloud_settings(self):
        data = self.get_api_request_kcl_azure("DEFENDER_SETTINGS")
        with self.Session() as session:
            for i in data["value"]:
                try:
                    settings = DefenderForCloudSettings()
                    settings.date = datetime.datetime.now().date()
                    settings.name = i.get("name")
                    settings.kind = i.get("kind")
                    settings.enabled = i.get("properties", {}).get("enabled")
                    session.add(settings)
                finally:
                    session.commit()

    def azure_operational_insights(self):
        data = self.get_api_request_kcl_azure("AZURE_INSIGHTS")
        with self.Session() as session:
            for i in data["value"]:
                try:
                    insights = azureOperationalInsightsOperations()
                    insights.date = datetime.datetime.now().date()
                    insights.name = i.get("name")
                    insights.provider = i.get("display", {}).get("provider")
                    insights.resource = i("display", {}).get("resource")
                    insights.operation = i.get("display", {}).get("operation")
                    insights.description = i.get("display", {}).get("description")
                    session.add(insights)
                    session.commit()
                finally:
                    session.close()

    def production_backups(self):
        pass

    def azure_web_apps(self):
        data = self.get_api_request_kcl_azure("AZURE_WEB_APPS")
        with self.Session() as session:
            for i in data["value"]:
                try:
                    azurewebapps = azureWebApps()
                    azurewebapps.date = datetime.datetime.now().date()
                    azurewebapps.name = i.get("name")
                    azurewebapps.type = i.get("type")
                    azurewebapps.kind = i.get("kind")
                    azurewebapps.location = i.get("location")
                    azurewebapps.environment = i.get("tags", {}).get(
                        "Environment", "No Data"
                    )
                    azurewebapps.application = i.get("tags").get(
                        "Application", "No Data"
                    )
                    azurewebapps.tier = i.get("tags", {}).get("Tier", 0)
                    azurewebapps.firewall = i.get("tags", {}).get("Firewall", 0)
                    azurewebapps.department = i.get("tags").get("Department", "No Data")
                    azurewebapps.costcentre = i.get("tags", {}).get("Cost Centre", 0)
                    azurewebapps.state = i.get("properties", {}).get("state", "No Data")
                    azurewebapps.hostnames = i.get("properties", {}).get(
                        "hostNames", "No Data"
                    )
                    azurewebapps.usagestate = i.get("properties", {}).get(
                        "usageState", "No Data"
                    )
                    azurewebapps.computemode = i.get("properties", {}).get(
                        "computeMode", "No Data"
                    )
                    azurewebapps.storagerecoverydefaultstate = i.get(
                        "properties", {}
                    ).get("storageRecoveryDefaultState", "No Data")
                    azurewebapps.deploymentid = i.get("properties", {}).get(
                        "deploymentId", "No Data"
                    )
                    azurewebapps.sku = i.get("properties", {}).get("sku", "No Data")
                    azurewebapps.inboundipaddress = i.get("properties", {}).get(
                        "inboundIpAddress", "No Data"
                    )
                    azurewebapps.resourcegroup = i.get("properties", {}).get(
                        "resourceGroup", "No Data"
                    )
                    session.add(azurewebapps)
                    session.commit()
                finally:
                    session.close()
                    
