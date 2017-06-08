#!/usr/bin/python

import time
import logging
import os
import sys
import subprocess
import datetime
import re
import socket
import json
import sender

graylog_server = sender.graylog_server()
graylog_port = sender.graylog_input_port()
files_to_read = sender.logs_to_read()
ip_address = socket.gethostbyname(socket.gethostname())
hostname = socket.gethostname()
today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
pysender_logdir = '/var/log/pysender'

if not os.path.isdir(pysender_logdir):
    os.mkdir('/var/log/pysender')

logger = logging.getLogger('pysender')
logger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address = (graylog_server, graylog_port), socktype = socket.SOCK_STREAM)
formatter = logging.Formatter(hostname + ' - %(message)s')

print(graylog_server, graylog_port, files_to_read, ip_address, hostname, today_date)


