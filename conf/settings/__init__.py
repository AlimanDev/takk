import os

DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'LOCAL')

if DEVELOPMENT_MODE == 'PRODUCTION':
    from .production import *
elif DEVELOPMENT_MODE == 'DEVELOPER':
    from .developer import *
else:
    from .local import *
