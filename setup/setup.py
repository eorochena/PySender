#!/usr/bin/env python3

import subprocess

#Create log directory for this application

subprocess.Popen('mkdir /var/log/pysender'.strip(), shell=True)