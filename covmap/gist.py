"""Data importing from LoRaWAN-based gps logger to gist geojson."""

import logging
import argparse
import json
import time
import re
import logging
import base64

import paho.mqtt.client as mqtt
from simplegist import Simplegist
import geojson

import arf8084
import ghgeojson


logger = logging.getLogger(__name__)


def on_connect(client, userdata, flags, rc):
    logger.info("Connected: %d", rc)
    client.subscribe('nodes/%s/packets' % userdata['neui'], 0)


def on_message(client, userdata, msg):
    logger.debug("msg arrives: %r", msg)
    dp = json.loads(msg.payload)
    gist_push(dp, userdata['map'], userdata['gist'],
              userdata['gistid'], userdata['geui'])


def on_subscribe(client, userdata, mid, granted_qos):
    logger.info("subscribed: %s, granted_qos: %s", mid, granted_qos)


def on_log(client, userdata, level, buf):
    logger.debug("log: %s, buf: %s", level, buf)


# http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
def camel2underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def gist_push(dp, map_, gist, gistid, geui):
    dp_ = {}
    for k, v in dp.iteritems():
        if k == 'datarate':  # fix naming discrepancy
            dp_['dataRate'] = v

        dp_[camel2underscore(k)] = v

    logger.debug("dp: %r", dp)

    if not geui or dp_['gateway_eui'] in geui:
        d = arf8084.decode(base64.b64decode(dp_['data']))
        logger.debug("decoded %s", d)
        if 'lat_lon' not in d:
            logger.info("gps data doesn't exist in %r", dp_['data'])
            return

        dp_.update(d)

        f = ghgeojson.feature(dp_)

        feature_hashes = set([x['properties']['hash']
                              for x in map_['features']])

        if f['properties']['hash'] not in feature_hashes:
            map_['features'].append(f)
            updated = geojson.dumps(map_, indent=4, sort_keys=True)
            logger.debug("updated %r", updated)
            gist.profile().edit(id=gistid,
                                content=updated)
        else:
            logger.warning("ignoring duplicated %s", f['properties']['hash'])


def fileimport(map_, gist, gistid, args):
    for f in json.loads(open(args.file, 'r').read()):
        gist_push(f, map_, gist, gistid, args.geui)


def mqttdaemon(map_, gist, gistid, args):
    client = mqtt.Client(userdata={'neui': args.neui,
                                   'geui': sorted(args.geui),
                                   'gist': gist,
                                   'gistid': gistid,
                                   'map': map_})
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_log = on_log

    client.connect(args.broker_host, args.broker_port, args.broker_keepalive)
    client.loop_forever()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count')

    parser.add_argument('--neui', required=True, help='node eui of gps')
    parser.add_argument('--geui', action='append', default=[],
                        help='enable gateway eui filtering, multiple allowed')
    parser.add_argument('--gist-secret', default=False, action='store_true',
                        help='make secret gists')
    parser.add_argument('--gist-suffix',
                        help='suffix added to the gist file name')
    parser.add_argument('--gist-user',
                        help='suffix added to the gist file name')
    parser.add_argument('--gist-token',
                        help='suffix added to the gist file name')

    sp = parser.add_subparsers()
    mqttp = sp.add_parser('mqtt', help=('daemon mode real-time '
                                        'importing from mqtt broker'))
    mqttp.add_argument('broker_host', help='mqtt broker host address',
                       metavar='HOST')
    mqttp.add_argument('--broker-port', help='mqtt broker tcp port',
                       default=1883, metavar='PORT')
    mqttp.add_argument('--broker-keepalive', default=60,
                       help='mqtt broker keep alive check interval in sec')
    mqttp.set_defaults(func=mqttdaemon)

    filep = sp.add_parser('import',
                          help='import from json file')
    filep.add_argument('file', help='input file name')
    filep.set_defaults(func=fileimport)

    return parser.parse_args()


def main():
    args = parse_args()

    loglevel = logging.WARNING
    if args.verbose == 1:
        loglevel = logging.INFO
    elif args.verbose >= 2:
        loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel)

    geui = sorted(args.geui)
    nparts = ['coverage']
    if geui:
        nparts.append('_'.join(geui))
    nparts.append(args.neui)
    if args.gist_suffix is not None:
        nparts.append(args.gist_suffix)
    gist_filename = '-'.join(nparts) + '.geojson'

    gist_cred = {}
    if args.gist_user is not None:
        gist_cred['username'] = args.gist_user
    if args.gist_token is not None:
        gist_cred['api_token'] = args.gist_token
    gist = Simplegist(**gist_cred)

    gistid = gist.profile().getMyID(gist_filename)
    if isinstance(gistid, int) and gistid == 0:
        gist.create(name=gist_filename, description='gps logger points',
                    content=geojson.dumps(geojson.FeatureCollection([])),
                    public=not args.gist_secret)
        gistid = gist.profile().getMyID(gist_filename)

    res = gist.profile().content(id=gistid)
    map_ = geojson.loads(res)

    args.func(map_, gist, gistid, args)


if __name__ == '__main__':
    main()
