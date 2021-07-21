#!/usr/bin/env python3
# Backup postgres database and upload zipped archive to yandex drive

import configparser
import subprocess

import zipfile
import datetime
import os

import yadisk

config = configparser.ConfigParser()
config.read('config.ini')

# Get Database backup via pg_dump
user = config['Global']['User']
password = config['Global']['Password']
host = config['Global']['Host']
port = config['Global']['Port']
database = config['Global']['Database']
output_filename = config['Global']['OutputFilename']
archive_password = config['Global']['ArchivePassword']

# Subprocess - run pg_dump
result = subprocess.run(['pg_dump', 'postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, database)], stdout=subprocess.PIPE)
# result in string decoded format
result_str_backup = result.stdout.decode('utf-8')
# Temporary save decoded str to file
with open('database_backup.bak', 'w') as f:
    f.write(result_str_backup)

# Create archive
archive_name = "%s.zip" % datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
system = subprocess.Popen(["7z", "a", archive_name, 'database_backup.bak', '-p{}'.format(archive_password)])
system.communicate()

# Upload archive to yandex disk
YaID = config['Yadisk']['YaID']
YaSecret = config['Yadisk']['YaSecret']
YaToken = config['Yadisk']['YaToken']

y = yadisk.YaDisk(YaID, YaSecret, YaToken)
y.upload(archive_name, '/%s' % archive_name)

# Remove zip archive from filesystem
os.remove('database_backup.bak')
os.remove(archive_name)
