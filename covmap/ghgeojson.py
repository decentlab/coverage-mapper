"""https://github.com/gonzalocasas/ttn-coverage-tracker"""

import hashlib

import crcmod
import geojson

API_ENCODING = 'utf-8'


crc8 = crcmod.predefined.mkPredefinedCrcFun('crc-8')


def feature(data_point):
    data_point_id = (data_point['gateway_time'] +
                     data_point['gateway_eui']).encode(API_ENCODING)
    data_point_hash = hashlib.sha1(data_point_id).hexdigest()

    point = geojson.Point((data_point['lat_lon'][1], data_point['lat_lon'][0]))
    props = dict(hash=data_point_hash, gateway_eui=data_point['gateway_eui'],
                 time=data_point['gateway_time'], rssi=data_point['rssi'],
                 snr=data_point['lsnr'], datarate=data_point['datarate'])

    # Add styling features
    # https://help.github.com/articles/mapping-geojson-files-on-github/
    props['marker-symbol'] = get_marker_symbol(data_point)
    props['marker-color'] = get_marker_color(data_point)

    return geojson.Feature(geometry=point, properties=props)


def get_marker_symbol(data_point):
    eui = data_point['gateway_eui']

    symbol = chr((crc8(eui) % 26) + 97)  # hopefully unique key for geui
    return symbol


def get_marker_color(data_point):
    try:
        rssi = float(data_point['rssi'])
    except:
        return color

    color = '#7d8182'  # default to grey

    if rssi < 0 and rssi >= -70:
        color = '#005a32'
    if rssi < -70:
        color = '#238443'
    if rssi < -90:
        color = '#41ab5d'
    if rssi < -100:
        color = '#78c679'
    if rssi < -110:
        color = '#addd8e'
    if rssi < -115:
        color = '#d9f0a3'

    return color
