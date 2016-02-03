"""decode gps data format from Adeunis-RF ARF8084 BA"""

import logging
import struct


TEMP_BIT = 7
ACC_BIT = 6
BTN_BIT = 5
GPS_BIT = 4
UPCNTR_BIT = 3
DOWNCNTR_BIT = 2
BATTERY_BIT = 1
RSSISNR_BIT = 0


logger = logging.getLogger(__name__)


DECODE_MAP = [(TEMP_BIT, 'b', lambda x: x, 'temperature'),
              # (ACC_BIT, '', lambda x: x, 'accelerometer_triggered'),
              # (BTN_BIT, '', lambda x: x, 'button_pressed'),
              (GPS_BIT, '8s', lambda x: (gpslat_frombcd(x[:4]),
                                         gpslon_frombcd(x[4:])), 'lat_lon'),
              (UPCNTR_BIT, 'B', lambda x: x, 'up_counter'),
              (DOWNCNTR_BIT, 'B', lambda x: x, 'down_counter'),
              (BATTERY_BIT, 'H', lambda x: x / 1000.0, 'battery_voltage'),
              (RSSISNR_BIT, '2s', lambda x: (x), 'rssi_sinr')]


def gps_todec(hem, deg, min=0, sec=0):
    return (deg + min / 60.0 + sec / 3600.0) * (-2 * hem + 1)


def gpslat_frombcd(bcd):
    assert len(bcd) == 4
    num = [ord(x) for x in bcd]
    deg = (num[0] >> 4) * 10.0 + (num[0] & 0xf)
    min = ((num[1] >> 4) * 10.0 + (num[1] & 0xf) +
           (num[2] >> 4) / 10.0 + (num[2] & 0xf) / 100.0 +
           (num[3] >> 4) / 1000.0)
    hem = num[3] & 1
    return gps_todec(hem, deg, min)


def gpslon_frombcd(bcd):
    assert len(bcd) == 4
    num = [ord(x) for x in bcd]
    deg = (num[0] >> 4) * 100.0 + (num[0] & 0xf) * 10.0 + (num[1] >> 4)
    min = ((num[1] & 0xf) * 10.0 + (num[2] >> 4) +
           (num[2] & 0xf) / 10.0 + (num[3] >> 4) / 100.0)
    hem = num[3] & 1
    return gps_todec(hem, deg, min)


def decode(data):
    logger.debug("decoding data: %r", data)
    present = [spec
               for spec
               in DECODE_MAP
               if (ord(data[0]) & (1 << spec[0])) != 0]

    fmt = '>' + ''.join(x[1] for x in present)
    items = struct.unpack(fmt, data[1:])
    decoded = ((name, fun(bytes))
               for (_, _, fun, name), bytes
               in zip(present, items))
    return dict(decoded)
