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

def upload_visualization(digest, segment, ioBuff):
    try:
        get_bucket()
        blob = storage.Blob('{}/{}'.format(digest, segment), bucket=bucket)
        blob.upload_from_file(ioBuff, content_type='image/png')
        blob.make_public()
        url = blob.public_url
    except BaseException as e:
        print('Failed to Generate Visualization - {}'.format(e))
        url = ''

    return url
