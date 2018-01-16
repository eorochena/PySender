#!/usr/bin/env python3

import json
import cloghandler
import logging
import logging.config
import os
import subprocess
import requests
import sender

graylog_server = sender.graylog_server()
load_balancer_port = int(sender.load_balancer_port())
admin_user = sender.graylog_admin_user()
admin_password = sender.graylog_admin_password()
servers = []
results = []
journal_capacity = []
facility = 'graylog-api'

logging.config.fileConfig('../conf/logging.conf')
log = logging.getLogger()

def graylog_state():
    try:
        response = requests.get('http://%s:%s/system/lbstatus' % (graylog_server, load_balancer_port),
                                timeout = 18, headers={'Connection':'close'})
        if response.text == 'ALIVE':
            try:
                response = requests.get('http://%s:%s/cluster' % (graylog_server, load_balancer_port),
                                            timeout = 18, headers={'Connection':'close'},
                                            auth = (admin_user, admin_password))
                val = json.loads(response.text)
                for i in val:
                    servers.append(i)
                for i in range(len(servers)):
                    if val[servers[i]]['is_processing'] == True:
                        results.append('True')
                        continue
                    elif val[servers[i]]['is_processing'] == False:
                        results.append('False')
                        continue
                if 'False' in results:
                    log.critical('%s GrayLog is not processing incoming messages' % facility)
                    return False
                else:
                    for i in range(len(servers)):
                        try:
                            response = requests.get('http://%s:%s/cluster/%s/journal'
                                                    % (graylog_server, load_balancer_port, servers[i]),timeout = 18,
                                                    headers = {'Connection':'close'},
                                                    auth = (admin_user, admin_password))
                            journal_status = json.loads(response.text)
                            journal_usage = (float(journal_status['journal_size'])/
                                             float(journal_status['journal_size_limit']))*100
                            if journal_usage >= 75:
                                journal_capacity.append(journal_usage)
                            elif journal_usage <= 74:
                                continue
                        except Exception as error:
                            log.critical('%s CRITICAL - unable to get journal status - %s' % (facility, error))
                            return False
                    if journal_capacity:
                            log.critical('%s CRITICAL - journal capacity = %s' % (facility, str(journal_capacity)))
                            return False
                    else:
                        return True
            except Exception as error:
                log.critical('%s CRITICAL - unable to get status response from GrayLog - %s' % (facility, error))
                return False
        else:
            log.critical('%s CRITICAL - Bad response from GrayLog - %s %s', (facility, response.content,
                                                                             response.status_code))
            return False
    except Exception as error:
        log.critical('%s CRITICAL - unable to get any response from GrayLog - %s ' % (facility, error))
        return False

