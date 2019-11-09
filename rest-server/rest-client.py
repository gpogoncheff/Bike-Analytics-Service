from __future__ import print_function
import requests
import json
import argparse
from time import perf_counter


def submit_datafile(address, file_dest):
    # prepare headers for http request
    headers = {'content-type': 'application/octet-stream'}
    data = open(file_dest, 'rb').read()

    # send http request with image and receive response
    filename = str(file_dest).split('/')[-1]
    submit_url = addr + '/upload_ride/{}'.format(filename)
    response = requests.put(submit_url, data=data, headers=headers)

    # decode response
    print("Response is", response)
    print(json.loads(response.text))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lab 6 Client Argument Parser')
    parser.add_argument('address')
    parser.add_argument('api')
    parser.add_argument('data_dest')
    args = parser.parse_args()

    addr = 'http://{}:5000'.format(args.address)

    if args.api == 'data':
        submit_datafile(addr, args.data_dest)
