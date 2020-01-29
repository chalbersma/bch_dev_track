#!/usr/bin/env python3

'''
Creates a class that can be used to represent a Project
'''

import os
import logging

import requests
import yaml

import tracker

class Project:

    # Plan was Published on Jan 22
    # This block was found on Jan 23
    # Only things at or higher this Block should Count
    _epoch_block = 619000

    _satoshify_factor = 100000000

    _def_file = "etc/recipients.yaml"
    _price_api_full = "https://api.exchange.bitcoin.com/api/2/public/ticker/BCHUSD"


    '''
    The Project Class
    '''

    def __init__(self, pkey=None, **kwargs):

        self.logger = logging.getLogger("tracker.Project")

        if pkey is None:
            raise ValueError("No pkey Specified")

        self.price = self.get_price()

        self.pkey = pkey

        self.name = kwargs.get("name", None)
        self.site = kwargs.get("site", None)
        self.source = kwargs.get("source", None)
        self.proj_type = kwargs.get("proj_type", None)
        self.campaigns_def = kwargs.get("campaigns", dict())
        self.campaigns = list()

        if kwargs.get("lfd", False) is True:
            self.def_file = kwargs.get("def_file", self._def_file)

            self.load_from_disk()

        self.total = 0

        self.validate()

        self.populate_campaigns()

    def usd_equiv(self, is_float=False):

        '''
        USD Equivalent
        '''

        total_in_bch = self.total / self._satoshify_factor

        price_per = float(self.price["last"])

        self.logger.debug("BCH: {} / USD Price {}".format(total_in_bch, price_per))

        if is_float is True:
            usd_equiv = total_in_bch * price_per
        else:
            usd_equiv = "${:,.2f}".format(total_in_bch * price_per)


        return usd_equiv


    def populate_campaigns(self):

        for campaign, this_camp_def in self.campaigns_def.items():

            self.logger.debug("Processing Campaign {} in {}".format(campaign, self.pkey))

            this_campaign = tracker.Campaign(cname=campaign,
                                             items=this_camp_def,
                                             since_height=self._epoch_block)

            # In Satoshis
            self.total += this_campaign.balance

            self.campaigns.append(this_campaign)

    def load_from_disk(self):

        '''
        Load all the Items from Disk and Choose the one noted in pkey
        '''

        if os.path.isfile(self.def_file) is True:
            try:
                with open(self.def_file, "r") as def_file_obj:
                    all_defs = yaml.safe_load(def_file_obj)
                    my_def = all_defs[self.pkey]
                    self.logger.debug(my_def)
            except Exception as read_defs_error:
                self.logger.error("Unable to Read definitions.")
                raise read_defs_error
            else:

                self.name = my_def["name"]
                self.site = my_def["site"]
                self.source = my_def["source"]
                self.proj_type = my_def["proj_type"]
                self.campaigns_def = my_def.get("campaigns", dict())


        else:
            self.logger.error("Unable to find file {}".format(self.def_file))
            raise FileNotFoundError()

    def get_price(self):

        '''
        Reach out to Bitcoin.com And Get Price Data
        '''

        response_data = None

        try:
            response = requests.get(self._price_api_full)
        except Exception as api_error:
            self.logger.error("Unable to TX for Coinbase Data {}".format(self.cname))
        else:

            if response.status_code == requests.codes.ok:
                response_data = response.json()

        return response_data

    def validate(self):

        '''
        Todo
        '''

        return True

    
