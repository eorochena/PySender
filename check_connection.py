#!/usr/bin/python3

import socket
import datetime
import os
import sys
import subprocess
import sender

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
        log_file = open(LogFile, 'a+')
        log_file.write(hoy + ' GrayLog connection lost \n')
        log_file.close()
        return True
    except Exception as error:
        log_file = open(LogFile, 'a+')
        log_file.write(hoy + ' - socket - Unable to establish connection with GrayLog - ' + str(error) + '\n')
        log_file.close()
        return False
print(status())