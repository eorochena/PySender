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
hostname = socket.gethostname()
today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
pysender_logdir = '/var/log/pysender'


def pysender(filename, app, firestart_pid):
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
                log_it = open(log_file(app), 'a+')
                log_it.write(today_date + ' - tail process appears not to be runnning properly - %s - %s\n' %
                             (filename, app))
                log_it.close()
                return False
        except Exception as error:
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            log_it = open(log_file(app), 'a+')
            log_it.write(today_date + ' - tail process appears not to be runnning properly - %s - %s\n' %
                             (filename, app))
            log_it.close()
            return False


    def firestart_status(app, firestart_pid):
        try:
            os.kill(firestart_pid, 0)
        except OSError:
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            log_it = open(log_file(app), 'a+')
            log_it.write(today_date + ' - firestart process is not running \n')
            log_it.close()
            return False
        else:
            return True


    def logmsg(app):
        content = ''
        while True:
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            msg = tail_it.stdout.readline()
            try:
                if len(msg) > 0 and len(content) <= 109186:
                    #if re.search(r'^[0-9]', msg) and re.search(r'(\d+-\d+-\d+)', msg):
                    yield content
                    content = msg
                    #else:
                    #   content += msg
                elif len(content) > 109186:
                    log_it = open(log_file(app), 'a+')
                    log_it.write('%s - Too many characters in message string\n' % today_date)
                    log_it.close()
                    continue
                else:
                    break
            except Exception as e:
                log_it = open(log_file(app), 'a+')
                log_it.write(today_date + ' - failed to process log message - ' + str(e) + '\n')
                log_it.close()
                continue
        if len(content) > 0:
            yield content

    today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    log_it = open(log_file(app), 'a+')
    log_it.write(today_date + ' - Starting application or at least trying - \n')
    log_it.close()


    while True:
        if tail_alive(filename, app) and check_connection.status() and graylog_status.graylog_state():
            sender = socket.socket()
            sender.connect_ex((graylog_server, graylog_port))
            try:
                for line in logmsg(app):
                    message = app + ' ' + str(json.dumps('%s' % line)) + '\n'
                    sender.sendall((message).encode('utf-8'))
            except Exception as error:
                today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                log_it = open(log_file(app), 'a+')
                log_it.write(today_date + ' - unable to send message to GrayLog - ' + str(error) + '\n')
                log_it.close()
                sender.close()
                continue
        elif tail_alive(filename, app) == False and check_connection.status() and graylog_status.graylog_state():
            tail_it = subprocess.Popen(['tail', '-F', filename], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            log_it = open(log_file(app), 'a+')
            log_it.write(today_date + ' - restarting tail_it\n')
            log_it.close()
            continue
        elif tail_alive(filename, app) and check_connection.status() == False and graylog_status.graylog_state():
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            log_it = open(log_file(app), 'a+')
            log_it.write(today_date + ' - Unable to send log messages to Graylog, Graylog Input is not processing '
                                      'incoming messages check /var/log/pysender/check_connection.log, '
                                      'retrying every 10 seconds\n')
            log_it.close()
            sender.close()
            time.sleep(10)
            continue
        elif tail_alive(filename, app) and check_connection.status() and graylog_status.graylog_state() == False:
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            log_it = open(log_file(app), 'a+')
            log_it.write(today_date + ' - Not sending messages to Graylog, incoming messages check '
                                      '/var/log/pysender/graylog_status.log, retrying every 10 seconds\n')
            log_it.close()
            time.sleep(10)
            continue
        elif tail_alive(filename, app) == False and graylog_status.graylog_state() == False and \
                        check_connection.status() == False:
            sys.exit(1)


if __name__ == '__main__':
    pysender(filename, app, firestart_pid)

