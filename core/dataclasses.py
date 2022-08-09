# Imports
from dataclasses import dataclass


@dataclass(frozen=True)
class ModRoles:
    mod: str = 'BotMod'
    admin: str = 'BotAdmin'
