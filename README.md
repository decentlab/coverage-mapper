Coverage mapper
===============
This tool converts gps logger data (Adeunis-RF ARF8084 BA) received from LoRaWAN network (thingsnetwork.org) to geojson format, and pushes it to a github gist for visualizing the map.

- Development stage
- Supports python 2.7

Installation
------------
```
$ pip install git+https://github.com/decentlab/coverage-mapper
```
Running
-------
There are two operating modes:

1. Import from json file:
  ```
  $ cmgist --gist-token YOUR_TOKEN --gist-user YOUR_USER --neui NEUI import datapoints.json
  ```

2. Receive in realtime from thingsnetwork.org using MQTT client:
  ```
  $ cmgist --gist-token YOUR_TOKEN --gist-user YOUR_USER --neui NEUI --gist-suffix test mqtt croft.thethings.girovito.nl
  ```
  
To stop the daemon, press Ctrl+C twice. For further information:
```
$ cmgist --help
```
References
----------
- https://github.com/gonzalocasas/ttn-coverage-tracker
- http://simplegist.readthedocs.org
