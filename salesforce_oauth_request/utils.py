import os
import re
import time
import base64
import urllib
import pickle
import os.path
import requests
from six.moves import range
from six.moves.urllib.parse import urlparse


def login(username=None,
          password=None,
          token=None,
          client_id=None,
          client_secret=None,
          redirect_uri="",
          state="",
          sandbox=False,
          cache_session=False):

    if 'HOME' in os.environ:
        cache_file = os.path.join(os.environ['HOME'], ".sf_oauth")
    else:
        cache_file = os.path.join(
            os.environ['HOMEDRIVE'],
            os.environ['HOMEPATH']
        )

    if cache_session and os.path.exists(cache_file):
        packet = read_cached_login(cache_file, username)
        if packet:
            return packet

    if token:
        r = token_login(username=username,
                        password=password,
                        token=token,
                        sandbox=sandbox,
                        client_id=client_id,
                        client_secret=client_secret)
    else:
        r = website_login(username=username,
                          password=password,
                          client_id=client_id,
                          client_secret=client_secret,
                          redirect_uri=redirect_uri,
                          sandbox=sandbox,
                          cache_session=cache_session,
                          state=state)

    if r.status_code < 300:
        packet = r.json()
        user_info = load_user_info(packet)
        packet.update(user_info)
        packet['endpoint'] = user_info['urls']['partner']
        if cache_session:
            write_cached_login(cache_file, username, packet)

        return packet
    else:
        return r.text


def token_login(username=None, password=None, token=None, client_id=None,
                client_secret=None, sandbox=None):

    client_id = os.environ.get('SALESFORCE_CLIENT_ID', client_id)
    client_secret = os.environ.get('SALESFORCE_CLIENT_SECRET', client_secret)

    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'format': 'json',
        'grant_type': 'password',
        'password': password + token,
        'username': username,
    }
    if sandbox:
        base = "https://test.salesforce.com"
    else:
        base = "https://login.salesforce.com"
    return requests.post(base + '/services/oauth2/token', params)


def website_login(username=None, password=None, client_id=None,
                  client_secret=None, redirect_uri=None, sandbox=None,
                  cache_session=None, state=None):
    if sandbox:
        base = "https://test.salesforce.com"
    else:
        base = "https://login.salesforce.com"

    auth_url = base + "/services/oauth2/authorize?"

    client_id = os.environ.get('SALESFORCE_CLIENT_ID', client_id)
    client_secret = os.environ.get('SALESFORCE_CLIENT_SECRET', client_secret)
    redirect_uri = os.environ.get('SALESFORCE_REDIRECT_URI', redirect_uri)

    auth_url += urllib.urlencode([
        ("response_type", "code"),
        ("display", "popup"),
        ("client_id", client_id),
        ("redirect_uri", redirect_uri),
        ("prompt", "login"),
        ("state", state)])

    s = requests.session()
    redirect_return = oauth_flow(
        s,
        auth_url,
        username=username,
        password=password,
        sandbox=sandbox,
    )

    # parse out the session id and endpoint
    params = urlparse.parse_qs(redirect_return)

    data = dict(code=params['code'],
                grant_type="authorization_code",
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                format="json")

    code_url = base + "/services/oauth2/token"
    return requests.post(code_url, data=data)


def oauth_flow(s, oauth_url, username=None, password=None, sandbox=False):
    """s should be a requests session"""
    r = s.get(oauth_url)
    if r.status_code >= 300:
        raise RuntimeError(r.text)

    params = urlparse.parse_qs(urlparse.urlparse(r.url).query)

    data = {
        "un": username,
        "width": 2560,
        "height": 1440,
        "hasRememberUn": True,
        "startURL": params['startURL'],
        "loginURL": "",
        "loginType": 6,
        "useSecure": True,
        "local": "",
        "lt": "OAUTH",
        "qs": "r=https%3A%2F%2Flocalhost%3A8443%2Fsalesforce%2F21",
        "locale": "",
        "oauth_token": "",
        "oauth_callback": "",
        "login": "",
        "serverid": "",
        "display": "popup",
        "username": username,
        "pw": password,
        "Login": "",
    }

    if sandbox:
        base = "https://test.salesforce.com"
    else:
        base = "https://login.salesforce.com"

    r2 = s.post(base, data)
    m = re.search("window.location.href\s*='(.[^']+)'", r2.text)
    assert m is not None, ("Couldn't find location.href expression in page {} "
                           "(Username or password is wrong)").format(r2.url)

    u3 = "https://" + urlparse.urlparse(r2.url).hostname + m.group(1)
    r3 = s.get(u3)

    m = re.search("window.location.href\s*='(.[^']+)'", r3.text)

    assert m is not None, ("Couldn't find location.href expression in page {}:"
                           "\n{}").format(r3.url, r3.text)

    return m.group(1)


def load_user_info(packet):
    data = dict(oauth_token=packet['access_token'], format="json")
    r = requests.post(packet['id'], data=data)
    if r.status_code >= 300:
        raise RuntimeError(r.text)
    else:
        user_info = r.json()
        partner = user_info['urls']['partner'].replace('{version}', '29')
        user_info['urls']['partner'] = partner
        return user_info


# Session caching

def write_cached_login(cache_file, username, packet):
    cache = _read_cached_logins(cache_file)
    cache[username] = packet
    _write_cached_logins(cache_file, cache)


def read_cached_login(cache_file, username):
    cache = _read_cached_logins(cache_file)
    return cache.get(username, None)


STORE_KEY = '38jfj&*Jshs*@&18930303jaaHAHAKAzh#H('


def _read_cached_logins(cache_file):
    if os.path.exists(cache_file):
        age = time.time() - os.path.getmtime(cache_file)
        if age < (60 * 60):
            try:
                return pickle.loads(
                    _decode(STORE_KEY, open(cache_file).read())
                )
            except IOError:
                return {}

    return {}


def _write_cached_logins(cache_file, cache):
    with open(cache_file, "w") as f:
        f.write(_encode(STORE_KEY, pickle.dumps(cache)))


# These are NOT SECURE, but at least we're not just storing plain text
def _encode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return base64.urlsafe_b64encode(encoded_string)


def _decode(key, string):
    decoded_chars = []
    string = base64.urlsafe_b64decode(string)
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(abs(ord(string[i]) - ord(key_c) % 256))
        decoded_chars.append(encoded_c)
    decoded_string = "".join(decoded_chars)
    return decoded_string
