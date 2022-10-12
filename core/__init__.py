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
__version_info__ = ('2022', '10', '11')  # Year.Month.Day
__version__ = '.'.join(__version_info__)
