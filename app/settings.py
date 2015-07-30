import os

PORT = int(os.environ.get('NOI_PORT', 80))
SECRET_KEY = os.environ.get('SECRET_KEY', 'M\xb5\xc1\xa39t\x97\x88\x13A\xe8\t\x90\xc2\x04@\xe4\xdeM\xc8?\x05}j')
LANG = os.environ.get('LANG', 'en')

