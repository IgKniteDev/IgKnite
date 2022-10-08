'''
Dataclasses to use across scripts.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


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
