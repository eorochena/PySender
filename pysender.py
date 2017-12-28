#!/usr/bin/env python3

import os
import subprocess
import datetime
import socket
import json
import sender
import sys
import time
import check_connection
import graylog_status

graylog_server = sender.graylog_server()
graylog_monitor_port = int(sender.monitor_port())
graylog_port = int(sender.graylog_input_port())
ip_address = socket.gethostbyname(socket.gethostname())
today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
pysender_logdir = '/var/log/pysender'


def pysender(filename, app, hostname):
    tail_it = subprocess.Popen(['tail', '-F', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def log_file(app):
        if not os.path.isdir(pysender_logdir):
            os.mkdir('/var/log/pysender')
        logging_file = pysender_logdir + '/pysender-%s.log' % app
        return logging_file


    def tail_alive(filename, app):
        try:
            if tail_it.poll() == None:
                return True
            else:
                today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                with open(log_file(app), 'a+') as log_it:
                    log_it.write(today_date + ' - tail process appears not to be runnning properly - %s - %s\n' %
                             (filename, app))
                return False
        except Exception as error:
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            with open(log_file(app), 'a+') as log_it:
                log_it.write(today_date + ' - tail process appears not to be runnning properly - %s - %s - %s\n' %
                             (filename, app, error))
            return False


    def firestart_status(app, firestart_pid):
        try:
            os.kill(firestart_pid, 0)
        except OSError:
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            with open(log_file(app), 'a+') as log_it:
                log_it.write(today_date + ' - firestart process is not running \n')
            return False
        else:
            return True


    def logmsg(app):
        content = ''
        while True:
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            msg = tail_it.stdout.readline()
            try:
                if len(msg) > 0 and len(msg) <= 109186:
                    yield content
                    content = msg
                elif len(msg) > 109186:
                    with open(log_file(app), 'a+') as log_it:
                        log_it.write('%s - Too many characters in message string\n' % today_date)
                    continue
                else:
                    break
            except Exception as e:
                with open(log_file(app), 'a+') as log_it:
                    log_it.write(today_date + ' - failed to process log message - ' + str(e) + '\n')
                continue
        if len(content) > 0:
            yield content

    today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    with open(log_file(app), 'a+') as log_it:
        log_it.write(today_date + ' - Starting application or at least trying - \n')


    while True:
        if tail_alive(filename, app) and check_connection.status() and graylog_status.graylog_state():
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            with open(log_file(app), 'a+') as log_it:
                log_it.write(today_date + ' - Sending messages to Graylog - \n')
            sender = socket.socket()
            sender.connect_ex((graylog_server, graylog_port))
            try:
                for line in logmsg(app):
                    message = hostname + ' - ' + app + ': ' + str(json.dumps('%s' % line)) + '\n'
                    sender.sendall((message).encode('utf-8'))
            except Exception as error:
                today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                with open(log_file(app), 'a+') as log_it:
                    log_it.write(today_date + ' - Unable to send message to Graylog - ' + str(error) + '\n')
                sender.close()
                continue
        elif tail_alive(filename, app) == False and check_connection.status() and graylog_status.graylog_state():
            tail_it = subprocess.Popen(['tail', '-F', filename], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            with open(log_file(app), 'a+') as log_it:
                log_it.write(today_date + ' - restarting tail_it\n')
            continue
        elif tail_alive(filename, app) and check_connection.status() == False and graylog_status.graylog_state():
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            with open(log_file(app), 'a+') as log_it:
                log_it.write(today_date + ' - Unable to send log messages to Graylog, Graylog Input is not processing '
                                      'incoming messages check /var/log/pysender/check_connection.log, '
                                      'retrying every 10 seconds\n')
            sender.close()
            time.sleep(10)
            continue
        elif tail_alive(filename, app) and check_connection.status() and graylog_status.graylog_state() == False:
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            with open(log_file(app), 'a+') as log_it:
                log_it.write(today_date + ' - Not sending messages to Graylog, incoming messages check '
                                      '/var/log/pysender/graylog_status.log, retrying every 10 seconds\n')
            time.sleep(10)
            continue
        elif tail_alive(filename, app) == False and graylog_status.graylog_state() == False and \
                        check_connection.status() == False:
            sys.exit(1)


if __name__ == '__main__':
    pysender(filename, app, hostname)

