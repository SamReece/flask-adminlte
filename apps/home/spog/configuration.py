import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.rdbms.postgresql import PostgreSQLManagementClient


def read_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def get_urls(url):
    config = read_json("cfg/configuration.json")
    endpoint = config["URLS"][url]
    return endpoint

def azure_access_token(scope):
    default_credential = DefaultAzureCredential()
    return default_credential.get_token(scope).token

def delete_kcl_database(subscription, resourcegroup, server, database):
    # use with caution
    # make sure you have a backup!
    # Do not run this against any production services
    # TO DO: hard code a parameter to break the function if 'Production' is detected
    client = PostgreSQLManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=subscription,
    )

    response = client.databases.begin_delete(
        resource_group_name=resourcegroup,
        server_name=server,
        database_name=database,
    ).result()
    print(response)
