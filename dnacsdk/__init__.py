import os.path
import sys

sys.path.append(os.path.dirname(__file__))

from .api import Api #, set_config, configure
from .exceptions import ResourceNotFound, UnauthorizedAccess, MissingConfig
