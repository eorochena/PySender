#!/usr/bin/env python

import os

conf_file = open('../conf/sender.conf', 'r')
read_it = conf_file.readlines()
parameters = {}

def file_location():
    for i in read_it:
        if 'file_location=' in i and i.find('#') == -1:
            parameters['file_location'] = i.split('"')[1]
    return parameters['file_location']


def ssl_enable():
    for i in read_it:
        if 'ssl_enable=' in i and i.find('#') == -1:
            parameters['ssl_enable'] = i.split('"')[1]
    return parameters['ssl_enable']


def ssl_cert():
    for i in read_it:
        if 'ssl_cert=' in i and i.find('#') == -1:
            parameters['ssl_cert'] = i.split('"')[1]
        elif 'ssl_cert=' in i and i.find('#') == 1:
            parameters['ssl_cert'] = 'None'
    return parameters['ssl_cert']


def graylog_server():
    for i in read_it:
        if 'server=' in i and i.find('#') == -1:
            parameters['server'] = i.split('"')[1]
    return parameters['server']

def monitor_port():
    for i in read_it:
        if 'monitor=' in i and i.find('#') == -1:
            parameters['monitor_port'] = i.split('"')[1]
    return parameters['monitor_port']

def graylog_input_port():
    for i in read_it:
        if 'port=' in i and i.find('#') == -1:
            parameters['port'] = i.split('"')[1]
    return parameters['port']


def load_balancer_port():
    for i in read_it:
        if 'load_balancer=' in i and i.find('#') == -1:
            parameters['lb_port'] = i.split('"')[1]
    return parameters['lb_port']


def graylog_admin_user():
    for i in read_it:
        if 'graylog_admin_user=' in i and i.find('#') == -1:
            parameters['graylog_admin_user'] = i.split('"')[1]
    return parameters['graylog_admin_user']


def graylog_admin_password():
    for i in read_it:
        if 'graylog_admin_password=' in i and i.find('#') == -1:
            parameters['graylog_admin_password'] = i.split('"')[1]
    return parameters['graylog_admin_password']


def logs_to_read():
    apps_log = {}
    for i in read_it:
        try:
            if 'application=' in i and i.find('#') == -1:
                parameters['application'] = i.split('"')[1]
                continue
            elif 'log_file=' in i and i.find('#') == -1 and os.path.isfile(i.split('"')[1]) == True:
                parameters['log_file'] = i.split('"')[1]
            apps_log[parameters['application']] = parameters['log_file']
        except:
            pass
    return apps_log

