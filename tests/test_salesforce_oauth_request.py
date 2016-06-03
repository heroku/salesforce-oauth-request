import os

import salesforce_oauth_request

USERNAME = None
PASSWORD = None
SECURITY_TOKEN = None
CONSUMER_KEY = None
CONSUMER_SECRET = None


def setup_module(module):
    global USERNAME, PASSWORD, SECURITY_TOKEN, CONSUMER_KEY, CONSUMER_SECRET

    # See `.travis.yml` on how this is set up.
    USERNAME = os.environ.get('SALESFORCE_USERNAME')
    PASSWORD = os.environ.get('SALESFORCE_PASSWORD')
    SECURITY_TOKEN = os.environ.get('SALESFORCE_SECURITY_TOKEN')
    CONSUMER_KEY = os.environ.get('SALESFORCE_CONSUMER_KEY')
    CONSUMER_SECRET = os.environ.get('SALESFORCE_CONSUMER_SECRET')

    environment_ready = USERNAME and PASSWORD and SECURITY_TOKEN and CONSUMER_KEY and CONSUMER_SECRET
    assert environment_ready, ("Make sure SALESFORCE_* environment variables pointing to "
                               "developer account are set. Check the test suite to find out more.")


def test_login():
    packet = salesforce_oauth_request.login(
        username=USERNAME,
        password=PASSWORD,
        client_id=CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        token=SECURITY_TOKEN,
    )

    assert packet['access_token'] is not None
    assert packet['username'] == USERNAME
