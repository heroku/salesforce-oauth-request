import os

import salesforce_oauth_request

VAR_NAMES = ['SALESFORCE_USERNAME', 'SALESFORCE_PASSWORD', 'SALESFORCE_SECURITY_TOKEN', 'SALESFORCE_CONSUMER_KEY', 'SALESFORCE_CONSUMER_SECRET']
CREDENTIALS = {x: None for x in VAR_NAMES}


def setup_module(module):
    global CREDENTIALS

    # See `.travis.yml` on how this is set up.
    for name in VAR_NAMES:
        CREDENTIALS[name] = os.environ.get(name)

    environment_ready = all(x for x in CREDENTIALS.values())
    assert environment_ready, ("Make sure SALESFORCE_* environment variables pointing to "
                               "developer account are set. Check the test suite to find out more.")


def test_login():
    packet = salesforce_oauth_request.login(
        username=CREDENTIALS['SALESFORCE_USERNAME'],
        password=CREDENTIALS['SALESFORCE_PASSWORD'],
        client_id=CREDENTIALS['SALESFORCE_CONSUMER_KEY'],
        client_secret=CREDENTIALS['SALESFORCE_CONSUMER_SECRET'],
        token=CREDENTIALS['SALESFORCE_SECURITY_TOKEN'],
    )

    assert packet['access_token'] is not None
    assert packet['username'] == CREDENTIALS['SALESFORCE_USERNAME']
