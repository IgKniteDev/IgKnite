# SPDX-License-Identifier: MIT


# Imports.
from os import system
from time import sleep

# This script acts as an automatic solution for restarting IgKnite in
# the event of an HTTP exception.
print('Blocked by HTTP exception, rebooting in 10 seconds...')
sleep(10)
system('python main..py')
