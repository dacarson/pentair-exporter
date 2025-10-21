
![Github License](https://img.shields.io/github/license/dacarson/pentair-exporter) 

# pentair-exporter

## Description
Export Pentair pool status to Influx DB so that it can be graphed with Grafana. To be run as a cron job.

Uses [screenlogicpy](https://github.com/dieselrabbit/screenlogicpy) python script to access the Pentair pool data.

As `screenlogicpy` creates deeply nested JSON objects and Influx DB only handles single depth Json objects, the objects that I am interested in are flattened in the function `publish_pentair_data`.
The following objects are created:
* Object for each **body** of water, eg Pool and Spa. The body objects contain Last_Temperature, Heat_Mode, Heat, Heat_Set_Point and Cool_Set_Point. For Heat_Mode, see enums defined in `screenlogicpy`
* Object for each **pump**. The pump object contains GPM_Now, RPM_Now and Watts_Now
* **Sensors** object, which contains each sensor and value
* **Circuits** object, which contains each configured circuit and value

## Usage
```
usage: pentair-exporter.py [-h] [-r] [--ip IP] [--influxdb] [--influxdb_host INFLUXDB_HOST] [--influxdb_port INFLUXDB_PORT] 
                        [--influxdb_user INFLUXDB_USER] [--influxdb_pass INFLUXDB_PASS] [--influxdb_db INFLUXDB_DB] 
                        [-v]

optional arguments:
  -h, --help            show this help message and exit
  -r, --raw             print json data to stddout
  --ip IP               IP address of Pentair ScreenLogic unit (skips discovery)
  --influxdb            publish to influxdb
  --influxdb_host INFLUXDB_HOST
                        hostname of InfluxDB HTTP API (default: localhost)
  --influxdb_port INFLUXDB_PORT
                        port of InfluxDB HTTP API (default: 8086)
  --influxdb_user INFLUXDB_USER
                        InfluxDB username
  --influxdb_pass INFLUXDB_PASS
                        InfluxDB password
  --influxdb_db INFLUXDB_DB
                        InfluxDB database name (default: pentair)
  -v, --verbose         verbose mode
  ````

### Discovery vs Direct IP Connection

The script supports two modes of operation:

1. **Auto-discovery mode** (default): The script automatically discovers Pentair ScreenLogic units on the network
2. **Direct IP mode**: Skip discovery and connect directly to a known IP address using the `--ip` option

#### Examples

**Auto-discovery mode:**
```bash
python3 pentair-exporter.py --influxdb --verbose
```

**Direct IP mode (faster, more reliable):**
```bash
python3 pentair-exporter.py --ip 192.168.1.100 --influxdb --verbose
```

**Raw data output with specific IP:**
```bash
python3 pentair-exporter.py --ip 192.168.1.100 --raw --verbose
```

### Cron Job Configuration

To configure as a cron job, `crontab -e`.

Recommend to run every 1 minutes, to not overload the controller.

**With auto-discovery:**
```bash
* * * * * /usr/bin/python3 /home/pi/pentair-exporter/pentair-exporter.py --influxdb --influxdb_user logger --influxdb_pass pass
```

**With direct IP (recommended for reliability):**
```bash
* * * * * /usr/bin/python3 /home/pi/pentair-exporter/pentair-exporter.py --ip 192.168.1.100 --influxdb --influxdb_user logger --influxdb_pass pass
```
  
  ## License

This content is licensed under [MIT License](https://opensource.org/license/mit/)
  
