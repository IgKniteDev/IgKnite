'''
The core package for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Initialize scripts.
from datetime import datetime

from . import chain as chain
from . import datacls as datacls
from .bot import *
from .embeds import *

# Set version number.
__version_info__ = ('2023', '3', '19')  # Year.Month.Day
__version__ = '.'.join(__version_info__)

# Set bot metadata.
BOT_METADATA = {
    'REPOSITORY': 'https://github.com/IgKniteDev/IgKnite',
    'DOCUMENTATION': 'https://igknition.ml/docs',
    'VERSION': __version__,
}

# Track uptime.
running_since = round(datetime.timestamp(datetime.now()))
