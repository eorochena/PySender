#!/usr/bin/python3

import cloghandler
import logging
import logging.config
import datetime
import os
import socket
import subprocess
import sender

graylog_server = sender.graylog_server()
graylog_monitor_port = int(sender.monitor_port())
port = int(sender.graylog_input_port())
facility = 'check_connection'
log_dir = "/var/log/pysender/"
logging.config.fileConfig('../conf/logging.conf')
log = logging.getLogger()

if os.path.isdir(log_dir) == False:
    log.info('Creating /var/log/pysender directory')
    subprocess.call('mkdir /var/log/pysender', shell=True)

def status():
    hoy = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    try:
        check_it = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        check_it.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        check_it.bind(('0.0.0.0', graylog_monitor_port))
        check_it.settimeout(12)
        check_it.connect((graylog_server, port))
        check_it.send('connected to GrayLog'.encode('utf-8'))
        check_it.shutdown(1)
        check_it.close()
        log.info('%s connected to Graylog input on port %s' % (facility, port))
        return True
    except Exception as error:
        log.critical('%s socket - Unable to establish connection with GrayLog - %s' % (facility, str(error)))
        return False
