import datetime
import logging

import azure.functions as func
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timezone
import os

from scrapers import scrapeNews

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.now(timezone.utc).astimezone().isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    jsonData = scrapeNews()

    # create blob service client and container client
    credential = DefaultAzureCredential()
    storage_account_url = "https://" + os.environ["par_storage_account_name"] + ".blob.core.windows.net"
    client = BlobServiceClient(account_url=storage_account_url, credential=credential)
    blob_name = "news" + str(datetime.now()) + ".txt"
    blob_client = client.get_blob_client(container=os.environ["par_storage_container_name"], blob=blob_name)
    blob_client.upload_blob(jsonData)
