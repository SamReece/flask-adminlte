from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient
from flask import jsonify
import json
from sqlalchemy.orm import sessionmaker
from spog.database import (
    kingsCollegeLondonRCSApplications
)
from sqlalchemy import Column, Integer, String, DateTime, create_engine
import pickle


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

def options():
    Session = sessionmaker(bind=postgresbind())
    with Session() as session:
        result = session.query(kingsCollegeLondonRCSApplications.name).all()
        data = json.dumps([dict(r) for r in result])
        apps = json.loads(data)
        return apps

def applicationSummary():
    Session = sessionmaker(bind=postgresbind())
    with Session() as session:
        result = session.query(kingsCollegeLondonRCSApplications).all()
        data = json.dumps([dict(r) for r in result])
        apps = json.loads(data)
        return jsonify(apps)

print(applicationSummary())