#!/usr/bin/env python3

import requests
import sys
import json
import sender
import logging

graylog_server = sender.graylog_server()
load_balancer_port = int(sender.load_balancer_port())
admin_user = sender.graylog_admin_user()
admin_password = sender.graylog_admin_password()
servers = []
results = []
journal_capacity = []

logging_file = "/var/log/pysender/graylog_status.log"
logging.basicConfig(format='%(asctime)s %(message)s', filename=logging_file, level=logging.INFO)

def graylog_state():
    try:
            response = requests.get('http://%s:%s/system/lbstatus' % (graylog_server, load_balancer_port),
                                timeout = 18, headers={'Connection':'close'})
            print(response.text)
            if response.text == 'ALIVE':
                    try:
                            response = requests.get('http://%s:%s/cluster' % (graylog_server, load_balancer_port),
                                                timeout = 18, headers={'Connection':'close'},
                                                auth = (admin_user, admin_password))
                            val = json.loads(response.text)
                            print(response.text)
                            print(val)
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
                                logging.critical('CRITICAL - GrayLog not processing ')
                                return False
                                sys.exit(1)
                            else:
                                for i in range(len(servers)):
                                    try:
                                        response = requests.get('http://%s:%s/cluster/%s/journal'
                                                % (graylog_server, load_balancer_port, servers[i]), timeout = 18,
                                                headers = {'Connection':'close'}, auth = (admin_user, admin_password))
                                        journal_status = json.loads(response.text)
                                        if (float(journal_status['journal_size'])/
                                                float(journal_status['journal_size_limit']))*100 >= 75:
                                            journal_capacity.append("BAD")
                                        elif (float(journal_status['journal_size'])/
                                                  float(journal_status['journal_size_limit']))\
                                                *100 <= 74:
                                            journal_capacity.append("GOOD")
                                    except Exception as error:
                                        logging.critical('4CRITICAL - unable to get journal status - %s' % error)
                                        return False
                                        sys.exit(1)
                                if 'BAD' in journal_capacity:
                                        logging.critical('CRITICAL - journal capacity = ' + \
                                            str((float(journal_status['journal_size'])
                                             /float(journal_status['journal_size_limit']))*100))
                                        return False
                                        sys.exit(1)
                                else:
                                        return True
                                        sys.exit(0)
                    except Exception as error:
                        logging.critical('3CRITICAL - unable to get response from GrayLog - %s' % error)
                        return False
                        sys.exit(1)
            else:
                logging.critical('2CRITICAL - Bad response from GrayLog - ', response.content, ' ', response.status_code)
                return False
                sys.exit(1)
    except Exception as error:
            logging.critical('1CRITICAL - unable to get any response from GrayLog - %s ' % error)
            return False
            sys.exit(1)

print(graylog_state())