#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import dateutil.parser

redis_host = '127.0.0.1'
redis_db = 0
redis_port = 6389

r = None


def __prepare():
    global r
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    r.ping()


def get_all_descriptions(asn):
    """
        Get all the descritpiosn available in the database for this ASN.
        Most recent first.

        :param asn: AS Number

        :rtype: List of tuples

            .. code-block:: python

                [
                    (datetime.datetime(), 'description 1'),
                    (datetime.datetime(), 'description 2'),
                    ...
                ]
    """
    all_descrs = r.hgetall(asn)
    dates = sorted(list(all_descrs.keys()), reverse=True)
    to_return = []
    for date in dates:
        d = dateutil.parser.parse(date)
        to_return.append((d, all_descrs[date]))
    return to_return


def get_last_description(asn):
    """
        Get only the most recent description.

        :param asn: AS Number

        :rtype: String
    """
    all_descrs = r.hgetall(asn)
    if len(all_descrs) == 0:
        return None
    dates = sorted(all_descrs.keys())
    return all_descrs[dates[-1]]


def get_last_update():
    """
        Return the last Update.

        :rtype: String, format: YYYYMMDD
    """
    last_update = r.get('last_update')
    if last_update is not None:
        return dateutil.parser.parse(last_update)
    return None


def get_all_updates():
    """
        Get all the updates processed.

        :rtype: List of Strings, Format: YYYYMMDD
    """
    all_updates = sorted(r.smembers('all_timestamps'), reverse=True)
    if len(all_updates) == 0:
        return None
    to_return = []
    for u in all_updates:
        to_return.append(dateutil.parser.parse(u))
    return to_return
