'''
The core package for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Initialize scripts.
from datetime import datetime

from . import datacls as datacls
from . import global_ as global_
from .bot import *
from .embeds import *
from .global_ import Secrets

# Set version number.
__version_info__ = ('2022', '10', '30')  # Year.Month.Day
__version__ = '.'.join(__version_info__)

# Set bot metadata.
BOT_METADATA = {
    'REPOSITORY': 'https://github.com/IgKniteDev/IgKnite',
    'DOCUMENTATION': 'https://igknition.ml/docs',
    'VERSION': __version__,
}

# Track uptime.
running_since = round(datetime.timestamp(datetime.now()))

# Load secrets.
secrets = Secrets()
