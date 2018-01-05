#!/usr/bin/env python3

import json
import logging.config
import socket
import subprocess
import sys
import time
import check_connection
import graylog_status
import sender

graylog_server = sender.graylog_server()
graylog_monitor_port = int(sender.monitor_port())
graylog_port = int(sender.graylog_input_port())
ip_address = socket.gethostbyname(socket.gethostname())
logging.config.fileConfig('../conf/logging.conf')
log = logging.getLogger()

def pysender(filename, app, hostname):
    facility = 'pysender-%s' % app
    tail_it = subprocess.Popen(['tail', '-F', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def tail_alive(filename, app):
        try:
            if tail_it.poll() == None:
                return True
            else:
                log.warning('%s tail process appears not to be runnning properly - %s - %s\n' % (facility,
                                                                                                 filename, app))
                return False
        except Exception as error:
            log.warning('%s tail process appears not to be runnning properly - %s - %s - %s\n' % (facility, filename,
                                                                                                  app, error))
            return False

    def logmsg():
        content = ''
        while True:
            msg = tail_it.stdout.readline()
            try:
                if len(msg) > 0 and len(msg) <= 109186:
                    yield content
                    content = msg
                elif len(msg) > 109186:
                    log.warning('%s Too many characters in message string' % facility)
                    break
                else:
                    break
            except Exception as error:
                log.warning('%s failed to process log message - %s' % (facility, str(error)))
                continue
        if len(content) > 0:
            yield content

    log.info('%s Starting application or at least trying...' % facility)


    while True:
        if tail_alive(filename, app) and check_connection.status() and graylog_status.graylog_state():
            log.info('%s Sending messages to Graylog :)' % facility)
            sender = socket.socket()
            sender.connect_ex((graylog_server, graylog_port))
            try:
                for line in logmsg():
                    message = hostname + ' - ' + app + ': ' + str(json.dumps('%s' % line)) + '\n'
                    sender.sendall((message).encode('utf-8'))
            except Exception as error:
                log.warning('%s Unable to send message to Graylog - %s' % (facility, str(error)))
                sender.close()
                continue
        elif tail_alive(filename, app) == False and check_connection.status() and graylog_status.graylog_state():
            tail_it = subprocess.Popen(['tail', '-F', filename], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            log.warning('%s restarting tail process' % facility)
            continue
        elif tail_alive(filename, app) and check_connection.status() == False and graylog_status.graylog_state():
            log.warning('%s Unable to send log messages to Graylog, Graylog Input is not processing, retrying... ' % facility)
            sender.close()
            time.sleep(10)
            continue
        elif tail_alive(filename, app) and check_connection.status() and graylog_status.graylog_state() == False:
            log.warning('%s Not sending messages to Graylog, retrying...' % facility)
            time.sleep(10)
            continue
        elif tail_alive(filename, app) == False and graylog_status.graylog_state() == False and \
                        check_connection.status() == False:
            sys.exit(1)


if __name__ == '__main__':
    pysender(filename, app, hostname)

