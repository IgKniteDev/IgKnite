# SPDX-License-Identifier: MIT


# Imports.
from dataclasses import dataclass


# Decorate pre-existing classes with @dataclass .
@dataclass(frozen=True)
class LockRoles:
    '''
    A dataclass used for role-locking.
    '''

    mod: str = 'BotMod'
    admin: str = 'BotAdmin'
