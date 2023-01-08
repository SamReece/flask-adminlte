import datetime
import os

import requests
from requests.auth import HTTPBasicAuth
from sqlalchemy.orm import sessionmaker
from spog.database import (
    CloudAbilityActualSpend,
    CloudAbilityInventory,
    CloudAbilityPlatformViews,
    CloudAbilityScoreCardMetrics,
    CloudAbilityForecastDetail,
    CloudAbilityForecastGeneric,
    CloudAbilityForecastDetailByPlatform,
    CloudAbilityViews,
    CloudabilityFinancialYear,
    azure_cli_creds,
    postgresbind,
)
from spog.configuration import read_json
from spog.kcl import AzureKCLRCSResources


class ApptioResources(object):
    def __init__(self):
        self.Session = sessionmaker(bind=postgresbind())

    def get_kcl_apptio_api_key(self):
        key = azure_cli_creds("kclkeyrpsecretdevneu1", "CloudabilityAPI")
        return key

    def get_all_kcl_views_as_dict(self):
        config = read_json("cfg/configuration.json")
        endpoint = config["SYSTEM_SUMMARY"]["SYSTEMS"]
        dict = {}
        for i in endpoint:
            dict[i["name"]] = i["CloudAbilityViewID"]
        return dict

    def get_kcl_view_id(self, system):
        config = read_json("cfg/configuration.json")
        endpoint = config["SYSTEM_SUMMARY"]["SYSTEMS"]
        for i in endpoint:
            if i["name"] == system:
                return i["CloudAbilityViewID"]

    def get_platform_view_id(self, platform):
        config = read_json("cfg/configuration.json")
        endpoint = config["APPTIO"]
        for i in endpoint["PLATFORM"]:
            if i["name"] == platform:
                return i["view"]

    def get_api_request(self, url):
        headers = {"Accept": "application/json"}
        key = self.get_kcl_apptio_api_key()
        auth = HTTPBasicAuth(key, os.environ["APPTIO_PASSWORD"])
        request = requests.get(url, headers=headers, auth=auth)
        return request.json()

    def get_apptio_actual_spend(self):
        tools = AzureKCLRCSResources()
        viewManagement = self.get_all_kcl_views_as_dict()
        views = viewManagement.items()
        for k, v in views:
            if v != 0:
                uuid = tools.get_uuid(k)
                url = "https://api.cloudability.com/v3/forecast?basis=cash&monthsForward=12&monthsBack=12&viewId={}".format(
                    v
                )
                data = self.get_api_request(url)
                with self.Session() as session:
                    try:
                        for i in data["result"]["actual"]:
                            try:
                                apptio_actual_spend = CloudAbilityActualSpend()
                                apptio_actual_spend.view = v
                                apptio_actual_spend.system = k
                                apptio_actual_spend.uuid = uuid
                                apptio_actual_spend.month = i.get("month")
                                apptio_actual_spend.spend = i.get("spend")
                                session.add(apptio_actual_spend)
                                session.commit()
                            finally:
                                session.close()
                    except KeyError:
                        continue

    def get_apptio_forecast_generic(self):
        tools = AzureKCLRCSResources()
        viewManagement = self.get_all_kcl_views_as_dict()
        views = viewManagement.items()
        for k, v in views:
            if v != 0:
                uuid = tools.get_uuid(k)
                url = "https://api.cloudability.com/v3/forecast?basis=cash&monthsForward=12&monthsBack=12&viewId={}".format(
                    v
                )
                headers = {"Accept": "application/json"}
                key = self.get_kcl_apptio_api_key()
                auth = HTTPBasicAuth(key, os.environ["APPTIO_PASSWORD"])
                request = requests.get(url, headers=headers, auth=auth)
                data = request.json()
                with self.Session() as session:
                    try:
                        for i in data["result"]["forecastDetail"]:
                            try:
                                apptio_actual_spend = CloudAbilityForecastGeneric()
                                apptio_actual_spend.view = v
                                apptio_actual_spend.system = k
                                apptio_actual_spend.uuid = uuid
                                apptio_actual_spend.month = i.get("month")
                                apptio_actual_spend.lowerBound = i.get("lowerBound")
                                apptio_actual_spend.upperBound = i.get("upperBound")
                                apptio_actual_spend.spend = i.get("spend")
                                session.add(apptio_actual_spend)
                                session.commit()
                            finally:
                                session.close()
                    except KeyError:
                        continue

    def get_apptio_forecast_detail(self):
        tools = AzureKCLRCSResources()
        viewManagement = self.get_all_kcl_views_as_dict()
        views = viewManagement.items()
        for k, v in views:
            if v != 0:
                uuid = tools.get_uuid(k)
                url = "https://api.cloudability.com/v3/forecast?basis=cash&monthsForward=12&monthsBack=12&viewId={}".format(
                    v
                )
                headers = {"Accept": "application/json"}
                key = self.get_kcl_apptio_api_key()
                auth = HTTPBasicAuth(key, os.environ["APPTIO_PASSWORD"])
                request = requests.get(url, headers=headers, auth=auth)
                data = request.json()
                with self.Session() as session:
                    try:
                        for i in data["result"]["forecastDetail"]:
                            try:
                                apptio_actual_spend = CloudAbilityForecastDetail()
                                apptio_actual_spend.view = v
                                apptio_actual_spend.system = k
                                apptio_actual_spend.uuid = uuid
                                apptio_actual_spend.forecastServiceMonth = i.get(
                                    "month"
                                )
                                apptio_actual_spend.forecastServiceSpend = i.get(
                                    "spend"
                                )
                                apptio_actual_spend.forecastUsageFamily = i.get(
                                    "usageFamily"
                                )
                                apptio_actual_spend.forecastServiceName = i.get(
                                    "serviceName"
                                )
                                session.add(apptio_actual_spend)
                                session.commit()
                            finally:
                                session.close()
                    except KeyError:
                        continue

    def get_apptio_forecast_detail_by_platform(self):
        config = read_json("cfg/configuration.json")
        for i in config["APPTIO"]["PLATFORM"]:
            url = "https://api.cloudability.com/v3/forecast?basis=cash&monthsForward=12&monthsBack=12&viewId={}".format(
                i["view"]
            )
            headers = {"Accept": "application/json"}
            key = self.get_kcl_apptio_api_key()
            auth = HTTPBasicAuth(key, os.environ["APPTIO_PASSWORD"])
            request = requests.get(url, headers=headers, auth=auth)
            data = request.json()
            name = i.get("name")
            view = i.get("view")
            uuid = i.get("UUID")
            with self.Session() as session:
                for i in data["result"]["forecastDetail"]:
                    try:
                        apptio_actual_spend = CloudAbilityForecastDetailByPlatform()
                        apptio_actual_spend.view = view
                        apptio_actual_spend.system = name
                        apptio_actual_spend.uuid = uuid
                        apptio_actual_spend.forecastServiceMonth = i.get("month")
                        apptio_actual_spend.forecastServiceSpend = i.get("spend")
                        apptio_actual_spend.forecastUsageFamily = i.get("usageFamily")
                        apptio_actual_spend.forecastServiceName = i.get("serviceName")
                        session.add(apptio_actual_spend)
                        session.commit()
                    finally:
                        session.close()

    def get_apptio_scorecard_metrics(self):
        tools = AzureKCLRCSResources()
        viewManagement = self.get_all_kcl_views_as_dict()
        views = viewManagement.items()
        for k, v in views:
            if v != 0:
                uuid = tools.get_uuid(k)
                url = "https://api.cloudability.com/v3/scorecards?dimension=category4&duration=ten-day&viewId={}".format(
                    v
                )
                headers = {"Accept": "application/json"}
                key = self.get_kcl_apptio_api_key()
                auth = HTTPBasicAuth(key, os.environ["APPTIO_PASSWORD"])
                request = requests.get(url, headers=headers, auth=auth)
                data = request.json()
                if request.status_code != 422:
                    with self.Session() as session:
                        for i in data["result"]["records"]:
                            exists = (
                                session.query(CloudAbilityScoreCardMetrics)
                                .filter_by(id=i.get("id"))
                                .first()
                                is not None
                            )
                            try:
                                apptio_scorecard = CloudAbilityScoreCardMetrics()
                                apptio_scorecard.overallscore = i.get("overallScore")
                                apptio_scorecard.topcomputespend = i.get(
                                    "topComputeSpend"
                                )
                                apptio_scorecard.elasticityscore = i.get(
                                    "elasticityScore"
                                )
                                apptio_scorecard.pricingscore = i.get("pricingScore")
                                apptio_scorecard.system = k
                                apptio_scorecard.view = v
                                apptio_scorecard.uuid = uuid
                                session.add(apptio_scorecard)
                                session.commit()
                            finally:
                                session.close()

    def get_apptio_scorecard_metrics_by_platform(self):
        config = read_json("cfg/configuration.json")
        for i in config["APPTIO"]["PLATFORM"]:
            url = "https://api.cloudability.com/v3/scorecards?dimension=category4&duration=ten-day&viewId={}".format(
                i["view"]
            )
            headers = {"Accept": "application/json"}
            key = self.get_kcl_apptio_api_key()
            auth = HTTPBasicAuth(key, os.environ["APPTIO_PASSWORD"])
            request = requests.get(url, headers=headers, auth=auth)
            data = request.json()
            name = i["name"]
            view = i["view"]
            uuid = i["UUID"]
            with self.Session() as session:
                try:
                    for i in data["result"]["records"]:
                        try:
                            apptio_scorecard = CloudAbilityScoreCardMetrics()
                            apptio_scorecard.overallscore = i.get("overallScore")
                            apptio_scorecard.topcomputespend = i.get("topComputeSpend")
                            apptio_scorecard.elasticityscore = i.get("elasticityScore")
                            apptio_scorecard.pricingscore = i.get("pricingScore")
                            apptio_scorecard.system = name
                            apptio_scorecard.view = view
                            apptio_scorecard.uuid = uuid
                            session.add(apptio_scorecard)
                            session.commit()
                        finally:
                            session.close()
                except KeyError:
                    continue

    def import_kcl_views(self):
        url = "https://api.cloudability.com/v3/views"
        headers = {"Accept": "application/json"}
        key = self.get_kcl_apptio_api_key()
        auth = HTTPBasicAuth(key, os.environ["APPTIO_PASSWORD"])
        request = requests.get(url, headers=headers, auth=auth)
        data = request.json()
        with self.Session() as session:
            for i in data["result"]:
                apptio_views = CloudAbilityInventory()
                # We dont want any duplicates in this table
                exists = (
                    session.query(CloudAbilityInventory)
                    .filter_by(view=i.get("id"))
                    .first()
                    is not None
                )
                try:
                    if exists != True:
                        apptio_views.title = i.get("title")
                        apptio_views.view = i.get("id")
                        session.add(apptio_views)
                        session.commit()
                finally:
                    session.close()

    def cost_report_by_platform(self, platform, range):
        kcl_platform = self.get_platform_view_id(platform)
        end_date = datetime.datetime.now()
        end = end_date.strftime(("%Y-%m-%d"))
        start_date = end_date - datetime.timedelta(range)
        begin = start_date.strftime(("%Y-%m-%d"))
        key = self.get_kcl_apptio_api_key()
        if platform != 0:
            url = "https://api.cloudability.com/v3/reporting/cost/run?start_date={}&end_date={}&dimensions=vendor&metrics=unblended_cost&view_id={}".format(
                begin, end, kcl_platform
            )
            headers = {"Accept": "application/json"}
            auth = HTTPBasicAuth(key, os.environ["APPTIO_PASSWORD"])
            request = requests.get(url, headers=headers, auth=auth)
            data = request.json()
            with self.Session() as session:
                for i in data["results"]:
                    try:
                        apptio = CloudAbilityPlatformViews()
                        apptio.vendor = i.get("vendor")
                        apptio.platform = platform
                        apptio.cost = i.get("unblended_cost")
                        apptio.description = "Data between {} and {}".format(begin, end)
                        apptio.daterange = range
                        session.add(apptio)
                        session.commit()
                    finally:
                        session.close()

    def cost_report_by_system(self, range):
        tools = AzureKCLRCSResources()
        systems = tools.get_kcl_systems()
        key = self.get_kcl_apptio_api_key()
        for system in systems:
            resourcegroup = tools.get_resource_group(system)
            uuid = tools.get_uuid(system)
            view = self.get_kcl_view_id(system)
            end_date = datetime.datetime.now()
            end = end_date.strftime(("%Y-%m-%d"))
            start_date = end_date - datetime.timedelta(range)
            begin = start_date.strftime(("%Y-%m-%d"))
            if view != 0:
                url = "https://api.cloudability.com/v3/reporting/cost/run?start_date={}&end_date={}&dimensions=vendor&metrics=unblended_cost&view_id={}".format(
                    begin, end, view
                )
                headers = {"Accept": "application/json"}
                auth = HTTPBasicAuth(key, os.environ["APPTIO_PASSWORD"])
                request = requests.get(url, headers=headers, auth=auth)
                request.raise_for_status()
                if request.status_code != 204 or request.status_code != 504:
                    data = request.json()
                    with self.Session() as session:
                        for i in data["results"]:
                            try:
                                apptio = CloudAbilityViews()
                                apptio.vendor = i.get("vendor")
                                apptio.cost = i.get("unblended_cost")
                                apptio.system = system
                                apptio.resourcegroup = resourcegroup
                                apptio.uuid = uuid
                                apptio.description = "Data between {} and {}".format(
                                    begin, end
                                )
                                apptio.daterange = range
                                session.add(apptio)
                                session.commit()
                            finally:
                                session.close()

    def cost_since_financial_year(self, year):
        tools = AzureKCLRCSResources()
        systems = tools.get_kcl_systems()
        key = self.get_kcl_apptio_api_key()
        for system in systems:
            resourcegroup = tools.get_resource_group(system)
            uuid = tools.get_uuid(system)
            view = self.get_kcl_view_id(system)
            begin = "{}-07-01".format(year)
            end_date = datetime.datetime.now()
            end = end_date.strftime(("%Y-%m-%d"))
            if view != 0:
                url = "https://api.cloudability.com/v3/reporting/cost/run?start_date={}&end_date={}&dimensions=vendor&metrics=unblended_cost&view_id={}".format(
                    begin, end, view
                )
                headers = {"Accept": "application/json"}
                auth = HTTPBasicAuth(key, os.environ["APPTIO_PASSWORD"])
                request = requests.get(url, headers=headers, auth=auth)
                data = request.json()
                with self.Session() as session:
                    for i in data["results"]:
                        try:
                            apptio = CloudabilityFinancialYear()
                            apptio.vendor = i.get("vendor")
                            apptio.cost = i.get("unblended_cost")
                            apptio.system = system
                            apptio.resourcegroup = resourcegroup
                            apptio.uuid = uuid
                            apptio.description = "Data between {} and {}".format(
                                begin, end
                            )
                            apptio.daterange = year
                            session.add(apptio)
                            session.commit()
                        finally:
                            session.close()
