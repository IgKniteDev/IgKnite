'''
The core package for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Initialize scripts.
from . import datacls as datacls, global_ as global_
from .bot import *
from .embeds import *


# Set version number.
__version_info__ = ('2022', '10', '18')  # Year.Month.Day
__version__ = '.'.join(__version_info__)


# Metadata
BOT_METADATA = {
    'REPOSITORY': 'https://github.com/IgKniteDev/IgKnite',
    'DOCUMENTATION': 'https://igknition.ml/docs',
    'VERSION': __version__,
}
