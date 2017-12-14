#!/usr/bin/env python3

import multiprocessing
import graylog_status
import logging
import os
import pysender
import socket
import sender
import subprocess
import check_connection
import sys
import datetime

files_to_read = sender.logs_to_read()
graylog_input_port = sender.graylog_input_port()
graylog_monitor_port = sender.monitor_port()
graylog_lb_port = int(sender.load_balancer_port())
graylog_server = sender.graylog_server()
firestart_pid = os.getpid()

## Application log
logging_file = "/var/log/pysender/firestart.log"
logging.basicConfig(format='%(asctime)s %(message)s', filename=logging_file, level=logging.INFO)

if os.path.isdir('/var/log/pysender') == False:
    subprocess.call('mkdir /var/log/pysender', shell=True)

emptiness = os.devnull
empty_file = open(emptiness, 'w')
ip_address = socket.gethostbyname(socket.gethostname())
hostname = socket.gethostname()


def graylog_api_status():
    if 'Alive' in graylog_status.graylog_state():
        return True
    else:
        logging.critical('CRITICAL - unable to connect to graylog api - %s\n' % graylog_status)


def start_pysender():
    def cmd(filename, app, firestart_pid):
        print(filename, app, firestart_pid)
        subprocess.Popen(pysender.pysender(filename, app, firestart_pid), stdout=empty_file, stderr=empty_file)

    def run():
        processes = []
        if processes:
            for process in processes:
                process.terminate()
            processes = []
        for log_file in files_to_read:
            app = log_file
            start_it = multiprocessing.Process(name = app, target = cmd, args = (files_to_read[log_file],
                                                                                 app, firestart_pid),)
            start_it.daemon = True
            processes.append(start_it)
        for i in range(len(files_to_read)):
            processes[i].start()
        for i in range(len(files_to_read)):
            processes[i].join()
        return processes
    return run()


while True:
    if check_connection.status() and graylog_status.graylog_state():
        today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        log_it = open(logging_file, 'a+')
        log_it.write(today_date + ' - Started application')
        log_it.close()
        start_pysender()
    else:
        today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        log_it = open(logging_file, 'a+')
        log_it.write(today_date + ' - CRITICAL - Failed to start application')
        log_it.close()
        sys.exit(1)
