#!/usr/bin/env python3

'''
Load a Campaing, Compute it's Totals (if asked)
'''

import logging
import urllib.parse

import requests

class Campaign:

    '''
    Campaign

    Load an Individual Campaign
    '''

    # It is a bad idea to only rely on one service
    _tx_api_base = "https://rest.bitcoin.com/v2/address/transactions/"
    _block_api_base = "https://rest.bitcoin.com/v2/block/detailsByHeight/"
    _satoshify_factor = 100000000

    def __init__(self, cname=None, items=dict(), **kwargs):

        '''
        Initialize the Campaign
        '''

        self.logger = logging.getLogger("tracker.Campaign")

        self.since_height = kwargs.get("since_height", 619000)

        self.cname = cname

        self.reason = items.get("reason", "unspecified")
        self.address = items.get("address", None)

        self.legacy_address = None
        self.cash_address = None

        self.transactions = list()

        self.balance = self.read_balance()

        self.credit_transactions()

    def credit_transactions(self):

        '''
        Enhance Transactions with Additional Data If Warranted
        '''

        for this_tx in list():
            # Check if Coinbase

            this_tx["img"] = None
            this_tx["who"] = None
            this_tx["who_url"] = None
            this_tx["reason"] = None

            if this_tx["coinbase"] is True:

                this_api_call = urllib.parse.urljoin(self._block_api_base,
                                                     urllib.parse.quote(this_tx["height"]))

                try:
                    response = requests.get(this_api_call)
                except Exception as api_error:
                    self.logger.error("Unable to TX for Coinbase Data {}".format(self.cname))
                else:

                    if response.status_code == requests.codes.ok:
                        response_data = response.json()

                        this_tx["img"] = "https://cdn4.iconfinder.com/data/icons/mining-worker-miner-labor/248/mining-worker-001-512.png"
                        this_tx["who"] = response_data.get("poolInfo", dict()).get("poolName", "Unknown Miner")
                        this_tx["who_url"] = response_data.get("poolInfo", dict()).get("url", "https://www.thewho.com/")
                        this_tx["reason"] = None
            else:
                # Normal Transaction
                # Someday Add Ability to Read and Credit OpReturn Data
                pass

    def read_balance(self):

        '''
        Read Balances
        '''

        api_call = urllib.parse.urljoin(self._tx_api_base,
                                        urllib.parse.quote(self.address))

        current_page = 0
        max_page = None

        return_bal_sats = 0

        height_okay = True

        while height_okay:
            try:
                response = requests.get(api_call,
                                        params={"page" : current_page})
            except Exception as api_error:
                self.logger.error("Unable to Query Data for Campaign {}".format(self.cname))
            else:

                if response.status_code == requests.codes.ok:
                    response_data = response.json()
                    # If First Time Let's Set
                    if max_page is None:
                        max_page = int(response_data.get("pagesTotal", 0))

                    if self.legacy_address is None:
                        self.legacy_address = response_data.get("legacyAddress")

                    if self.cash_address is None:
                        self.cash_address = response_data.get("cashAddress")

                    # Blocks Come in In Descending Oder
                    for this_tx in response_data.get("txs", ()):
                        this_tx_obj = {"txid" : this_tx["txid"],
                                       "coinbase" : False,
                                       "height" : int(this_tx.get("blockheight")),
                                       "given" : 0}

                        if "coinbase" in this_tx["vin"][0].keys():
                            this_tx_obj["coinbase"] = True

                        if this_tx_obj["height"] > self.since_height:
                            for this_vout in this_tx["vout"]:
                                possible_addresses = this_vout.get("scriptPubKey", dict()).get("addresses", list())
                                self.logger.debug(possible_addresses)
                                if self.legacy_address in possible_addresses:
                                    # This output is going to my address
                                    this_tx_out_sats = int(float(this_vout["value"]) * self._satoshify_factor)
                                    return_bal_sats += this_tx_out_sats
                                    this_tx_obj["given"] += this_tx_out_sats

                                    self.logger.info("{} Adding tx with {} sats at height {}".format(self.cname,
                                                                                                     this_tx_obj["given"],
                                                                                                     this_tx_obj["height"]))

                                    self.transactions.append(this_tx_obj)

                        else:
                            self.logger.debug("Reached end of Epoch for {} at Height {} ({})".format(self.cname,
                                                                                                     this_tx_obj["height"],
                                                                                                     self.since_height))

                            height_okay = False

                            # This breaks me out of the For loop but the height_okay will break me out of the while loop
                            break

                else:
                    # Address Find Error Let's Exit
                    break
            finally:
                if max_page == current_page:
                    break
                else:
                    current_page += 1

        return return_bal_sats



