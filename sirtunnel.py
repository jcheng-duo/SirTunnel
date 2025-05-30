#!/usr/bin/env python3

import argparse
import sys
import json
import time
from urllib import request


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--tls', action='store_true')
    parser.add_argument('--insecure', action='store_true')
    parser.add_argument('host')
    parser.add_argument('port')
    args = parser.parse_args(sys.argv[1:])

    host = args.host
    port = args.port
    tunnel_id = host + '-' + port

    caddy_add_route_request = {
        "@id": tunnel_id,
        "match": [{
            "host": [host],
        }],
        "handle": [{
            "handler": "reverse_proxy",
            "upstreams":[{
                "dial": ':' + port
            }]
        }]
    }

    if args.tls:
        tls_options = {}
        if args.insecure:
            tls_options['insecure_skip_verify'] = True
        caddy_add_route_request['handle'][0]['transport'] = {"protocol": "http", "tls": tls_options}

    body = json.dumps(caddy_add_route_request).encode('utf-8')
    headers = {
        'Content-Type': 'application/json'
    }
    create_url = 'http://127.0.0.1:2019/config/apps/http/servers/sirtunnel/routes'
    req = request.Request(method='POST', url=create_url, headers=headers)
    request.urlopen(req, body)

    print("Tunnel created successfully")

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:

            print("Cleaning up tunnel")
            delete_url = 'http://127.0.0.1:2019/id/' + tunnel_id
            req = request.Request(method='DELETE', url=delete_url)
            request.urlopen(req)
            break
