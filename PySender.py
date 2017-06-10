#!/usr/bin/python

import logging.handlers
import os
import subprocess
import datetime
import socket
import json
import sender
import Queue
import threading

graylog_server = sender.graylog_server()
graylog_port = int(sender.graylog_input_port())
files_to_read = sender.logs_to_read()
ip_address = socket.gethostbyname(socket.gethostname())
hostname = socket.gethostname()
today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
pysender_logdir = '/var/log/pysender'

logger = logging.getLogger('pysender')
logger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address = (graylog_server, graylog_port), socktype = socket.SOCK_STREAM)
formatter = logging.Formatter(hostname + ' - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def log_file(app):
    if not os.path.isdir(pysender_logdir):
        os.mkdir('/var/log/pysender')
    logging_file = pysender_logdir + '/' + app
    return logging_file

def tail_alive(filename, app):
    tail_pid = tail_it.pid
    alive = os.popen('ps ax|grep "tail -F %s"|grep -w "%s"|grep -v grep|wc -l' % (filename, tail_pid)).read()[0]
    if int(alive) >= 1:
        return True
    elif int(alive) < 1:
        log_it = open(log_file(app), 'a+')
        log_it.write(today_date + ' - tail process appears not to be runnning properly - %s - %s - %s\n' % (alive, filename, app))
        log_it.close()
        return False

def firestart_status(app):
    fire_alive = os.popen('ps ax|grep FireStart|egrep -v \'grep|log|defunct\'|awk \'{print $6}\'').read().rsplit()
    if fire_alive:
        if fire_alive[0].split('/')[-1]  == 'FireStart':
            return True
        else:
            log_it = open(log_file(app), 'a+')
            log_it.write(today_date + ' - FireStart process is not running - %s\n' % fire_alive)
            log_it.close()
            return False
    elif not fire_alive:
        log_it = open(log_file(app), 'a+')
        log_it.write(today_date + ' - FireStart process is not running - %s\n' % fire_alive)
        log_it.close()
        return False


def logmsg(filename, app):
    content = ''
    while True:
        msg = tail_it.stdout.readline()
        try:
            if len(msg) > 0 and len(content) <= 109186:
                #if re.search(r'^[0-9]', msg) and re.search(r'(\d+-\d+-\d+)', msg):
                yield content
                content = msg
                #else:
                 #   content += msg
            elif len(content) > 109186:
                today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                log_it = open(log_file(app), 'a+')
                log_it.write('%s - Too many characters in message string\n' % today_date)
                log_it.close()
                continue
            else:
                break
        except Exception, e:
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            log_it = open(log_file(app), 'a+')
            log_it.write(today_date + ' - failed to process log message - ' + str(e) + '\n')
            log_it.close()
            continue


def run_while(filename, app):
    while True:
        if tail_alive(filename, app) and firestart_status(app):
            try:
                for line in logmsg(filename, app):
                    message = app + ' ' + str(json.dumps('%s' % line)) + '\n'
                    logger.info(message)
            except Exception,e:
                today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                log_it = open(log_file(app), 'a+')
                log_it.write(today_date + ' - unable to send message to GrayLog - ' + str(e) + '\n')
                log_it.close()
        elif not tail_alive(filename, app) and firestart_status(app):
            tail_it = subprocess.Popen(['tail', '-F', filename], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            today_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            log_it = open(log_file(app), 'a+')
            log_it.write(today_date + ' - restarting tail_it\n')
            log_it.close()
            continue
        elif tail_alive(filename, app) and not firestart_status(app):
            break
        elif not tail_alive(filename, app) and not firestart_status(app):
            break

queue = Queue.Queue()
def run_wild(filename, app):
    queue.put(run_while(filename, app))

thread_names = {}
x = 0
for application in files_to_read:
    filename = files_to_read[application]
    app = application
    tail_it = subprocess.Popen(['tail', '-F', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    thread_names[application] = threading.Thread(target=run_while(filename, app))
    thread_names[application].daemon = True
    thread_names[application].start()
    print(x += 1)




