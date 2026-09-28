from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


STORAGE_ACCOUNT_NAME = "spacexdocuments"
CONTAINER_NAME = "spacex"

ACCOUNT_URL = (
    f"https://spacexdocuments.blob.core.windows.net"
)


def get_container_client():
    credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(
        account_url=ACCOUNT_URL,
        credential=credential,
    )

    return blob_service_client.get_container_client(
        CONTAINER_NAME
    )


def list_documents():
    container_client = get_container_client()

    blobs = container_client.list_blobs()

    return [blob.name for blob in blobs]


def download_document(blob_name):
    container_client = get_container_client()

    blob_client = container_client.get_blob_client(
        blob_name
    )

    data = blob_client.download_blob().readall()

    return data
