#!/usr/bin/python3

import datetime
import os
import socket
import subprocess

from pysender import sender

graylog_server = sender.graylog_server()
graylog_monitor_port = int(sender.monitor_port())
port = int(sender.graylog_input_port())

# Application log
LogDir = "/var/log/pysender/"
LogFile = "/var/log/pysender/check_connection.log"
today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
if os.path.isdir(LogDir) == False:
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
        with open(LogFile, 'a+') as log_file:
            log_file.write(hoy + ' Connected to Graylog input on port %s\n' % port)
        return True
    except Exception as error:
        with open(LogFile, 'a+') as log_file:
            log_file.write(hoy + ' - socket - Unable to establish connection with GrayLog - ' + str(error) + '\n')
        return False
