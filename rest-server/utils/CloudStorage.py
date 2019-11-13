from google.cloud import storage

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

def get_visualization_url(digest, segment):
    url = ''
    bucket = get_visualizations_bucket()
    blob = bucket.get_blob('{}/{}'.format(digest, segment))
    if blob:
        url = str(blob.public_url)
    return url
