#/usr/bin/python3

import asyncio
import logging
import argparse
import json
import time
import copy
from pprint import pprint

from screenlogicpy import ScreenLogicGateway, discovery

"""
usage: pentair-exporter.py [-h] [-r] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -r, --raw             print raw data to stddout
  --influxdb            publish to influxdb
  --influxdb_host INFLUXDB_HOST
                        hostname or ip of InfluxDb HTTP API
  --influxdb_port INFLUXDB_PORT
                        port of InfluxDb HTTP API
  --influxdb_user INFLUXDB_USER
                        InfluxDb username
  --influxdb_pass INFLUXDB_PASS
                        InfluxDb password
  --influxdb_db INFLUXDB_DB
                        InfluxDb database name
  -v, --verbose         verbose output to watch the threads
"""



#----------------

def influxdb_publish(event, data):
    from influxdb import InfluxDBClient

    if not data:
        print("Not publishing empty data for: ", event)
        return

    try:
        client = InfluxDBClient(host=args.influxdb_host,
                                port=args.influxdb_port,
                                username=args.influxdb_user,
                                password=args.influxdb_pass,
                                database=args.influxdb_db)

#remove second level JSON objects        
        clean_data = copy.deepcopy(data)

        clean_data['enum_options'] = ''
        clean_data['configuration'] = ''
        clean_data['color'] = ''

        payload = {}
        payload['measurement'] = event

        payload['time']   = int(time.time())
        payload['fields'] = clean_data

        if args.verbose:
            print ("publishing %s to influxdb [%s:%s]: %s" % (event,args.influxdb_host, args.influxdb_port, payload))

        # write_points() allows us to pass in a precision with the timestamp
        client.write_points([payload], time_precision='s')

    except Exception as e:
        print("Failed to connect to InfluxDB: %s" % e)
        print("  Payload was: %s" % payload)

#----------------
def publish_pentair_data(gateway):
    from screenlogicpy.device_const.system import BODY_TYPE 

    cur_data = gateway.get_data()
    if args.verbose:
        print("Publishing data")

    if args.raw:
        pprint(cur_data)

    if args.influxdb:
        influxdb_publish('pool_last_temperature', cur_data['body'][BODY_TYPE.POOL]['last_temperature'])
        influxdb_publish('pool_heat_mode', cur_data['body'][BODY_TYPE.POOL]['heat_mode'])
        influxdb_publish('pool_heat_status', cur_data['body'][BODY_TYPE.POOL]['heat_state'])
        influxdb_publish('pool_heat_set_point', cur_data['body'][BODY_TYPE.POOL]['heat_setpoint'])
        influxdb_publish('pool_cool_set_point', cur_data['body'][BODY_TYPE.POOL]['cool_setpoint'])
        influxdb_publish('spa_last_temperature', cur_data['body'][BODY_TYPE.SPA]['last_temperature'])
        influxdb_publish('spa_heat_mode', cur_data['body'][BODY_TYPE.SPA]['heat_mode'])
        influxdb_publish('spa_heat_status', cur_data['body'][BODY_TYPE.SPA]['heat_state'])
        influxdb_publish('spa_heat_set_point', cur_data['body'][BODY_TYPE.SPA]['heat_setpoint'])
        influxdb_publish('spa_cool_set_point', cur_data['body'][BODY_TYPE.SPA]['cool_setpoint'])
        influxdb_publish('pump_currentGPM', cur_data['pump'][0]['gpm_now'])
        influxdb_publish('pump_currentRPM', cur_data['pump'][0]['rpm_now'])
        influxdb_publish('pump_currentWatts', cur_data['pump'][0]['watts_now'])
        influxdb_publish('circuit_pool', cur_data['circuit'][505])
        influxdb_publish('circuit_spa', cur_data['circuit'][500])
        influxdb_publish('circuit_pool_light', cur_data['circuit'][501])
        influxdb_publish('circuit_spa_light', cur_data['circuit'][502])
        influxdb_publish('air_temperature', cur_data['controller']['sensor']['air_temperature'])
        influxdb_publish('salt_ppm', cur_data['controller']['sensor']['salt_ppm'])

#----------------

async def main():
    from screenlogicpy.const.msg import CODE

    #logging.basicConfig(
    #    format="%(asctime)s %(levelname)-8s %(message)s",
    #    level=logging.DEBUG,
    #    datefmt="%Y-%m-%d %H:%M:%S",
    #)
    if args.verbose:
        print("Looking for Pentair ScreenLogic units")

    hosts = await discovery.async_discover()
    while len(hosts) == 0:
        print("No Pentair ScreenLogic units found, looking again")
        hosts = await discovery.async_discover()

    print("Found "+str(len(hosts))+" units")

    if len(hosts) > 0:

        loop = asyncio.get_running_loop()

        connection_lost = loop.create_future()

        def on_connection_lost():
            connection_lost.set_result(True)

        def status_updated():
            if args.verbose:
                print("---- ** New Pool Data ** ----")

            #Force an update of Pump data as it doesn't seem to be updated otherwise
            # gateway.async_get_pumps()

            if args.influxdb:
                publish_pentair_data(gateway)

        def chemistry_updated_1():
            print("-- ** CHEMISTRY UPDATED 1 ** -")

        gateway = ScreenLogicGateway()

        await gateway.async_connect(
            **hosts[0], connection_closed_callback=on_connection_lost
        )

        # Multiple 'clients' can subscribe to different ScreenLogic messages
        data_unsub = await gateway.async_subscribe_client(
            status_updated, CODE.STATUS_CHANGED
        )
        chem_unsub1 = await gateway.async_subscribe_client(
            chemistry_updated_1, CODE.CHEMISTRY_CHANGED
        )

        # Create a baseline for pumps and scg data
        await gateway.async_update()

        # Do an initial update
        if args.influxdb:
            publish_pentair_data(gateway)
        if args.raw:
            pprint(gateway.get_data())

        try:
            await connection_lost
        finally:
            data_unsub()
            chem_unsub1()
            if args.raw:
                pprint(gateway.get_data())
            await gateway.async_disconnect()

    else:
        print("Should never hit this. No gateways found")



#----------------
if __name__ == "__main__":

    # argument parsing is u.g.l.y it ain't got no alibi, it's ugly !
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        """,
    )

    parser.add_argument("-r", "--raw",     dest="raw",     action="store_true", help="print json data to stddout")

    parser.add_argument("--influxdb",      dest="influxdb",      action="store_true",                                 help="publish to influxdb")
    parser.add_argument("--influxdb_host", dest="influxdb_host", action="store",      default="localhost",            help="hostname of InfluxDB HTTP API")
    parser.add_argument("--influxdb_port", dest="influxdb_port", action="store",      default=8086,         type=int, help="hostname of InfluxDB HTTP API")
    parser.add_argument("--influxdb_user", dest="influxdb_user", action="store",                                      help="InfluxDB username")
    parser.add_argument("--influxdb_pass", dest="influxdb_pass", action="store",                                      help="InfluxDB password")
    parser.add_argument("--influxdb_db",   dest="influxdb_db",   action="store",      default="pentair",              help="InfluxDB database name")

    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="verbose mode - show threads")

    args = parser.parse_args()

while (1):
	asyncio.run(main())
