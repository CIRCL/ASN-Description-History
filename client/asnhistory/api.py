#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import dateutil.parser


class ASNHistory(object):

    def __init__(self, host='127.0.0.1', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)
        self.r.ping()

    def get_all_descriptions(self, asn):
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
        all_descrs = self.r.hgetall(asn)
        dates = sorted(list(all_descrs.keys()), reverse=True)
        return [(dateutil.parser.parse(date), all_descrs[date]) for date in dates]

    def get_last_description(self, asn):
        """
            Get only the most recent description.

            :param asn: AS Number

            :rtype: String
        """
        all_descrs = self.r.hgetall(asn)
        if len(all_descrs) == 0:
            return None
        dates = sorted(all_descrs.keys())
        return all_descrs[dates[-1]]

    def get_last_update(self):
        """
            Return the last Update.

            :rtype: String, format: YYYYMMDD
        """
        last_update = self.r.get('last_update')
        if not last_update:
            return None
        return dateutil.parser.parse(last_update)

    def get_all_updates(self):
        """
            Get all the updates processed.

            :rtype: List of Strings, Format: YYYYMMDD
        """
        all_updates = sorted(self.r.smembers('all_timestamps'), reverse=True)
        if not all_updates:
            return None
        return [dateutil.parser.parse(u) for u in all_updates]
