import datetime

import requests
from sqlalchemy.orm import sessionmaker
from src.configuration import azure_access_token, read_json
from src.database import (
    KingsCollegeLondonResourceGroups,
    alertsbyResourceGroup,
    kingsCollegeLondonRCSApplications,
    KingsCollegeLondonResourceInventory,
    postgresbind,
)


class AzureKCLRCSResources(object):
    def __init__(self, scope=None, config=None, url=None):
        self.scope = scope
        self.url = url
        self.config = read_json("cfg/configuration.json")
        self.Session = sessionmaker(bind=postgresbind())

    def __str__(self):
        version = "0.1 - pre-alpha"
        author = "Sam Reece"
        association = "Kings College London"
        summary = {
            "Version": version,
            "Author": author,
            "Association": association,
            "Session": self.Session,
        }
        return summary

    def query_adopted_systems_in_database_all(self):
        with self.Session() as session:
            result = session.query(KingsCollegeLondonResourceGroups).all()
            for row in result:
                print("Name: ", row.applicationName)
                print("Resource Group: ", row.resourceGroup)
                print("-------")
            session.close()

    def query_adopted_systems_in_database_live(self):
        with self.Session() as session:
            result = session.query(KingsCollegeLondonResourceGroups).filter(
                KingsCollegeLondonResourceGroups.resourceGroup != "TBC"
            )
            for row in result:
                print("Name: ", row.applicationName)
                print("Resource Group: ", row.resourceGroup)
                print("-------")
            session.close()

    def query_adopted_systems_in_database_under_caf(self):
        with self.Session() as session:
            result = session.query(KingsCollegeLondonResourceGroups).filter(
                KingsCollegeLondonResourceGroups.resourceGroup == "TBC"
            )
            for row in result:
                print("Name: ", row.applicationName)
                print("Resource Group: ", row.resourceGroup)
                print("-------")
            session.close()

    def get_application_summary(self):
        config = read_json("cfg/configuration.json")
        endpoint = config["SYSTEM_SUMMARY"]["SYSTEMS"]
        return endpoint

    def get_resource_group(self, system):
        config = read_json("cfg/configuration.json")
        endpoint = config["SYSTEM_SUMMARY"]["SYSTEMS"]
        for i in endpoint:
            if i["name"] == system:
                return i["Resource Group"]

    def get_kcl_resources(self):
        config = read_json("cfg/configuration.json")
        endpoint = config["SYSTEM_SUMMARY"]["SYSTEMS"]
        dict = {}
        for i in endpoint:
            dict[i["name"]] = i["Resource Group"]
        return dict

    def get_kcl_systems(self):
        config = read_json("cfg/configuration.json")
        endpoints = config["SYSTEM_SUMMARY"]["SYSTEMS"]
        list = []
        for i in endpoints:
            list.append(i["name"])
        return list

    def get_kcl_inventory(self, system):
        config = read_json("cfg/configuration.json")
        endpoint = config["SYSTEM_SUMMARY"]["SYSTEMS"]
        for i in endpoint:
            if i["name"] == system:
                return i["azure inventory"]

    def get_uuid(self, system):
        config = read_json("cfg/configuration.json")
        endpoint = config["SYSTEM_SUMMARY"]["SYSTEMS"]
        for i in endpoint:
            if i["name"] == system:
                return i["UUID"]

    def get_kcl_applications(self):
        config = read_json("cfg/configuration.json")
        endpoint = config["SYSTEM_SUMMARY"]["SYSTEMS"]
        return endpoint

    def get_kcl_alerts_by_resource_group(self, application):
        config = read_json("cfg/configuration.json")
        endpoint = config["URLS"]["DEFENDER_ALERTS_BY_RG"]
        return endpoint.format(application)

    def get_urls_with_formatting(self, url, resourcegroup):
        config = read_json("cfg/configuration.json")
        endpoint = config["URLS"][url].format(resourcegroup)
        return endpoint

    def kings_college_london_application_summary(self):
        data = self.get_kcl_applications()
        with self.Session() as session:
            for i in data:
                kclApps = kingsCollegeLondonRCSApplications()
                # We dont want any duplicates in this table
                exists = (
                    session.query(kingsCollegeLondonRCSApplications)
                    .filter_by(name=i.get("name"))
                    .first()
                    is not None
                )
                try:
                    if exists != True:
                        kclApps.date = datetime.datetime.now().date()
                        kclApps.name = i.get("name")
                        kclApps.contact = i.get("contact")
                        kclApps.description = i.get("description")
                        kclApps.note = i.get("note")
                        kclApps.resourcegroup = i.get("Resource Group")
                        kclApps.uuid = i.get("UUID")
                        kclApps.azureinventory = i.get("azure inventory")
                        kclApps.cloudabilityviewid = i.get("CloudAbilityViewID")
                        session.add(kclApps)
                    else:
                        continue
                finally:
                    session.commit()
                session.close()

    def kcl_research_services_resource_groups(self):
        data = self.get_kcl_resources()
        kclResources = data.items()
        with self.Session() as session:
            for k, v in kclResources:
                try:
                    kclResourceGroups = KingsCollegeLondonResourceGroups()
                    kclResourceGroups.applicationName = k
                    kclResourceGroups.resourceGroup = v
                    session.add(kclResourceGroups)
                finally:
                    session.commit()
                    session.close()

    def kcl_resource_inventory_by_system(self):
        summary = self.get_application_summary()
        config = read_json("cfg/configuration.json")
        scope = config["SCOPES"]["MANAGEMENT"]
        token = azure_access_token(scope)
        payload = {"Authorization": "bearer " + token}
        with self.Session() as session:
            for i in summary:
                url = i.get("azure inventory")
                name = i.get("name")
                uuid = i.get("UUID")
                resourceGroup = i.get("Resource Group")
                if url != "TBC":
                    request = requests.get(url, headers=payload)
                    data = request.json()
                    for i in data["value"]:
                        try:
                            inventory = KingsCollegeLondonResourceInventory()
                            inventory.resourcegroup = resourceGroup
                            inventory.uuid = uuid
                            inventory.name = name
                            inventory.azure_id = i.get("id")
                            inventory.type = i.get("type")
                            inventory.location = i.get("location")
                            inventory.managedby = i.get("managedBy", "No Data")
                            inventory.skuName = i.get("sku", {}).get("name", "No Data")
                            inventory.skuTier = i.get("sku", {}).get("tier", "No Data")
                            inventory.sku_family = i.get("sku", {}).get(
                                "family", "No Data"
                            )
                            inventory.sku_capacity = i.get("sku", {}).get("capacity", 0)
                            inventory.environment = i.get("tags", {}).get(
                                "Environment", "No Data"
                            )
                            inventory.application = i.get("tags", {}).get(
                                "Application", "No Data"
                            )
                            inventory.department = i.get("tags", {}).get(
                                "Department", "No Data"
                            )
                            inventory.costcentre = i.get("tags", {}).get(
                                "Cost Centre", 0
                            )
                            inventory.firewall = i.get("tags", {}).get("Firewall", 0)
                            session.add(inventory)
                            session.commit()
                        finally:
                            session.close()

    def kcl_rsp_alerts_by_resource_group(self, application):
        config = read_json("cfg/configuration.json")
        scope = config["SCOPES"]["MANAGEMENT"]
        token = azure_access_token(scope)
        resourcegroup = self.get_resource_group(application)
        endpoint = self.get_kcl_alerts_by_resource_group(resourcegroup)
        uuid = self.get_uuid(application)
        payload = {"Authorization": "bearer " + token}
        request = requests.get(endpoint, headers=payload)
        data = request.json()
        with self.Session() as session:
            for i in data["value"]:
                try:
                    alertsbyresourcegroup = alertsbyResourceGroup()
                    alertsbyresourcegroup.resourcegroup = resourcegroup
                    alertsbyresourcegroup.name = i.get("name")
                    alertsbyresourcegroup.type = i.get("type")
                    alertsbyresourcegroup.uuid = uuid
                    alertsbyresourcegroup.status = i.get("properties", {}).get(
                        "status", "No Data"
                    )
                    alertsbyresourcegroup.compromisedentity = i.get(
                        "properties", {}
                    ).get("compromisedEntity", "No Data")
                    alertsbyresourcegroup.alerttype = i.get("properties", {}).get(
                        "alertType", "No Data"
                    )
                    alertsbyresourcegroup.timegenerated = i.get("properties", {}).get(
                        "timeGeneratedUtc", "No Data"
                    )
                    alertsbyresourcegroup.version = i.get("properties", {}).get(
                        "version", "No Data"
                    )
                    alertsbyresourcegroup.intent = i.get("properties", {}).get(
                        "intent", "No Data"
                    )
                    alertsbyresourcegroup.productname = i.get("properties", {}).get(
                        "productName", "No Data"
                    )
                    alertsbyresourcegroup.productcomponentname = i.get(
                        "properties", {}
                    ).get("productComponentName", "No Data")
                    alertsbyresourcegroup.severity = i.get("properties", {}).get(
                        "severity", "No Data"
                    )
                    alertsbyresourcegroup.alerturi = i.get("alertUri", "No Data")
                    alertsbyresourcegroup.isinicident = i.get("properties", {}).get(
                        "isIncident", "No Data"
                    )
                    session.add(alertsbyresourcegroup)
                    session.commit()
                finally:
                    session.close()
