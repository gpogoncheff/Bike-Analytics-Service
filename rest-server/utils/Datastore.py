from google.cloud import datastore

client = None

def get_client():
    global client
    if client is None:
        client = datastore.Client()
    return client

def get_ride_data(digest):
    client = get_client()
    query = client.query(kind='Ride')
    query.add_filter('digest', '=', digest)
    results = list(query.fetch())
    return [dict(item) for item in results]

def get_aggregate_statistics():
    client = get_client()
    query = client.query(kind='Ride')
    results = list(query.fetch())
    agg_data = {'total duration': 0, 'total distance': 0, 'total climb': 0, 'total descend': 0}
    for result in results:
        agg_data['total duration'] += result['duration']
        agg_data['total distance'] += result['distance']
        agg_data['total climb'] += result['climb']
        agg_data['total descend'] += result['descend']
    return agg_data

def get_ride_visualizations(digest):
    pass
