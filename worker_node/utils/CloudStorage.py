from google.cloud import storage
import io

client = None
bucket = None

def get_client():
    global client
    if client is None:
        client = storage.Client()
    return client

def get_bucket():
    global bucket
    if bucket is None:
        client = get_client()
        bucket = client.lookup_bucket('data-visualizations')
    return bucket

def upload_visualization(digest, segment):
    get_bucket()
    blob = storage.Blob('test0/item0', bucket=bucket)

    with open("testimage.jpg", "rb") as imageFile:
        str = imageFile.read()
        ioBuffer = io.BytesIO(str)
        blob.upload_from_file(ioBuffer, content_type='image/jpeg')
        blob.make_public()
        print(blob.public_url)
