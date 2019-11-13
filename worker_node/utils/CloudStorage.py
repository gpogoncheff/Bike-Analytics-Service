from google.cloud import storage
import io

client = None

def get_client():
    global client
    if client is None:
        client = storage.Client()
    return client

def get_visualizations_bucket():
    client = get_client()
    bucket = client.lookup_bucket('data-visualizations')
    return bucket

def get_ride_file_bucket():
    client = get_client()
    bucket = client.lookup_bucket('ride-files')
    return bucket

def upload_visualization(digest, segment, ioBuff):
    try:
        bucket = get_visualizations_bucket()
        blob = storage.Blob('{}/{}'.format(digest, segment), bucket=bucket)
        blob.upload_from_file(ioBuff, content_type='image/png')
        blob.make_public()
        url = blob.public_url
    except BaseException as e:
        print('Failed to upload visualization - {}'.format(e))
        url = ''
    return url

def upload_file(digest, filedata):
    try:
        bucket = get_ride_file_bucket()
        blob = storage.Blob('{}'.format(digest), bucket=bucket)
        blob.upload_from_string(filedata)
    except BaseException as e:
        print('Failed to upload ride file - {}'.format(e))
