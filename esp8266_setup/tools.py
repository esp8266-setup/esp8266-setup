import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import pwd
except ImportError:
    import getpass  
    pwd = None

def current_user():
    if pwd:
        return pwd.getpwuid(os.geteuid()).pw_name
    else:
        return getpass.getuser()

def replace_placeholders(template, **kwargs):
    template = template.replace('%year%', str(datetime.now().year))
    template = template.replace('%user%', current_user())
    for key, value in kwargs.items():
        template = template.replace('%' + key + '%', value)
    return template