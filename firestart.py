#!/usr/bin/env python3

import graylog_status
import os
import pysender
import socket
import sender
import check_connection
import sys
import datetime
import threading
import time

files_to_read = sender.logs_to_read()
graylog_input_port = sender.graylog_input_port()
graylog_monitor_port = sender.monitor_port()
graylog_lb_port = int(sender.load_balancer_port())
graylog_server = sender.graylog_server()
firestart_pid = os.getpid()

logging_file = "/var/log/pysender/firestart.log"

emptiness = os.devnull
empty_file = open(emptiness, 'w')
ip_address = socket.gethostbyname(socket.gethostname())
hostname = socket.gethostname()


def start_pysender():
    def cmd(filename, app, firestart_pid):
        pysender.pysender(filename, app, firestart_pid)

    def run():
        processes = []
        for log_file in files_to_read:
            app = log_file
            start_it = threading.Thread(name = app, target = cmd, args = (files_to_read[log_file],
                                                                                 app, hostname),)
            start_it.setDaemon(True)
            processes.append(start_it)
        for i in range(len(files_to_read)):
            processes[i].start()
            time.sleep(1)
        for i in range(len(files_to_read)):
            processes[i].join()
    return run()


while True:
    if check_connection.status() and graylog_status.graylog_state():
        today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        with open(logging_file, 'a+') as log_it:
            log_it.write(today_date + ' - Started application\n')
        start_pysender()
    else:
        today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        with open(logging_file, 'a+') as log_it:
            log_it.write(today_date + ' - CRITICAL - Failed to start application because either the Graylog input is not '
                                  ' active or rejecting trafic check /var/log/pysender/check_connection.log'
                                  ' or the Graylog api is not returning the expected results check '
                                  '/var/log/graylog_status.log\n')
        sys.exit(1)
