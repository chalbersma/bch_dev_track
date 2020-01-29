#!/usr/bin/env python3

import tracker
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("scratch")

start_block = 619000
duration = 144 * 236

# Jan 23 + 236 Days + 144 Blocks Per Day
expected_end_block = start_block + duration

# Why is this not dynamic? I hate myself sometimes
current_block_height = 619888

blocks_in = current_block_height - start_block

# 6 Million Goal
goal = 6000000

expected_percent = blocks_in / duration

expected_amount = goal * expected_percent

running_total_bch = 0
running_total = 0

for pkey in ["bu", "babc", "bchd", "bcash", "bverde", "flow", "electronc", "badger", "cashaddr"]:
    this_project = tracker.Project(pkey=pkey,
                                   lfd=True)

    print(this_project.campaigns_def)
    print(this_project.total)
    print(this_project.usd_equiv())

    running_total_bch += this_project.bch_equiv(is_float=True)
    running_total += this_project.usd_equiv(is_float=True)

actual_percent = running_total / goal


print("Grand Total ${:,.2f} / ₿ {:,.8f}".format(running_total, running_total_bch))
print("Actual Percent {:.4%}".format(actual_percent))
print("Expected Percent {:.4%}".format(expected_percent))
print("Expected Amount ${:,.2f}".format(expected_amount))
