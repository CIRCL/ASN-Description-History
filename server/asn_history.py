#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import dateutil.parser
import glob
import os
from pubsublogger import publisher
import re
import redis
import time
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

sleep_timer = 3600
redis_host = '127.0.0.1'
redis_db = 0
redis_port = 6389


def __prepare(directory):
    temp_dir = os.path.join(directory, 'temp')
    old_dir = os.path.join(directory, 'old')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    if not os.path.exists(old_dir):
        os.makedirs(old_dir)


def fetch(url, directory):
    temp_dir = os.path.join(directory, 'temp')
    old_dir = os.path.join(directory, 'old')

    filename = os.path.join(temp_dir, 'autnums.html')
    urlretrieve('http://www.cidr-report.org/as2.0/autnums.html', filename)
    f = open(filename).read()
    update_raw = re.sub('[\n()]', '',
                        re.findall('File last modified at (.*)</I>', f, re.S)[0])
    update = dateutil.parser.parse(update_raw).isoformat()

    newfile = os.path.join(directory, update)
    oldfile = os.path.join(old_dir, update)
    if os.path.exists(newfile) or os.path.exists(oldfile):
        os.remove(filename)
        return False
    else:
        os.rename(filename, newfile)
        publisher.info('File updated at ' + update)
        return True


def parse(directory):
    old_dir = os.path.join(directory, 'old')
    to_import = glob.glob(os.path.join(directory, '*'))
    to_import.sort()
    for f_name in to_import:
        if os.path.isdir(f_name):
            continue
        try:
            update = None
            f = open(f_name).read()
            data = re.findall('as=AS(.*)&.*</a> (.*)\n', f)
            update_raw = re.sub('[\n()]', '',
                                re.findall('File last modified at (.*)</I>', f, re.S)[0])
            update = dateutil.parser.parse(update_raw).isoformat()
            yield update, data
            os.rename(f_name, os.path.join(old_dir, update))
        except:
            publisher.info('Invalid file. Update:' + update)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import ASN descriptions.')

    parser.add_argument('-d', '--directory', type=str, default='autnums',
                        help='Directory where the files are saved.')
    parser.add_argument('-n', '--not_new', action='store_true',
                        help='Do not download new files from the website.')

    args = parser.parse_args()
    __prepare(args.directory)

    publisher.port = redis_port
    publisher.channel = 'ASN_History'
    time.sleep(5)
    publisher.info('Importer started.')
    while True:
        for timestamp, data in parse(args.directory):
            r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

            last_update = r.get('last_update')
            if last_update > timestamp:
                msg = 'Trying to import an old file (old). Latest: {new}'.format(
                    old=timestamp, new=last_update)
                publisher.error(msg)
                continue
            else:
                msg = '===== Importing new file: {new} ====='.format(new=timestamp)
                publisher.info(msg)
                p = r.pipeline(transaction=False)
                p.set('last_update', timestamp)
                p.sadd('all_timestamps', timestamp)
                new_asns = 0
                updated_descrs = 0
                for asn, descr in data:
                    all_descrs = r.hgetall(asn)
                    if len(all_descrs) == 0:
                        p.hset(asn, timestamp, descr)
                        publisher.debug('New asn: {asn}'.format(asn=asn))
                        new_asns += 1
                    else:
                        dates = sorted(all_descrs.keys())
                        last_descr = all_descrs[dates[-1]]
                        if descr != last_descr:
                            p.hset(asn, timestamp, descr)
                            msg = 'New description for {asn}. Was {old}, is {new}'.format(
                                asn=asn, old=last_descr, new=descr)
                            publisher.info(msg)
                            updated_descrs += 1
                p.execute()
                msg = '===== Import finished: {new}, new ASNs:{nb}, Updated:{up} ====='.format(
                    new=timestamp, nb=new_asns, up=updated_descrs)
                publisher.info(msg)
        if args.not_new:
            break
        else:
            newfile = False
            try:
                newfile = fetch('http://www.cidr-report.org/as2.0/autnums.html', args.directory)
            except:
                publisher.warning('Exception in fetching!')
            if not newfile:
                time.sleep(sleep_timer)
