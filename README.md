
![Github License](https://img.shields.io/github/license/dacarson/WeatherFlowApi) 

# pentair-exporter

## Description
Export Pentair pool status to Influx DB so that it can be graphed with Grafana. Written so that it could be used as a service.

Uses [screenlogicpy](https://github.com/dieselrabbit/screenlogicpy) python script to access the Pentair pool data.

As `screenlogicpy` creates deeply nested Json objects and Influx DB only handles single depth Json objects, the objects that I am interested in are flattened in the function `publish_pentair_data`.

## Usage
```
usage: pentair-async.py [-h] [-r] [--influxdb] [--influxdb_host INFLUXDB_HOST] [--influxdb_port INFLUXDB_PORT] 
                        [--influxdb_user INFLUXDB_USER] [--influxdb_pass INFLUXDB_PASS] [--influxdb_db INFLUXDB_DB] 
                        [-v]

optional arguments:
  -h, --help            show this help message and exit
  -r, --raw             print json data to stddout
  --influxdb            publish to influxdb
  --influxdb_host INFLUXDB_HOST
                        hostname of InfluxDB HTTP API
  --influxdb_port INFLUXDB_PORT
                        hostname of InfluxDB HTTP API
  --influxdb_user INFLUXDB_USER
                        InfluxDB username
  --influxdb_pass INFLUXDB_PASS
                        InfluxDB password
  --influxdb_db INFLUXDB_DB
                        InfluxDB database name
  -v, --verbose         verbose mode - show threads
  ````
  
  ## License

This content is licensed under [MIT License](https://opensource.org/license/mit/)
  
