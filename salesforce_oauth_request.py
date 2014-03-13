__author__ = 'spersinger'

import re
import urllib
import requests
import urlparse

def login(username = None, 
          password = None, 
          client_id = None, 
          client_secret = None, 
          redirect_uri="", 
          state="", 
          sandbox=False):
    base = "https://login.salesforce.com" if not sandbox else "https://test.salesforce.com"
    auth_url = base + "/services/oauth2/authorize?"

    auth_url += urllib.urlencode([
        ("response_type", "code"), 
        ("display", "popup"), 
        ("client_id",client_id),
        ("redirect_uri", redirect_uri), 
        ("prompt", "login"), 
        ("state", state)])

    s = requests.session()
    redirect_return = oauth_flow(s, auth_url, username=username, password=password)
    
    # parse out the session id and endpoint
    params = urlparse.parse_qs(redirect_return)

    data = dict(code=params['code'],
                grant_type="authorization_code",
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                format="json")

    code_url = base + "/services/oauth2/token"
    r = requests.post(code_url, data=data)
    if r.status_code < 300:
        return r.json()
    else:
        return r.text


def oauth_flow(s, oauth_url, username=None, password=None):
    """s should be a requests session"""
    r = s.get(oauth_url)
    if r.status_code >= 300:
        raise RuntimeError(r.text)

    params = urlparse.parse_qs(urlparse.urlparse(r.url).query)

    data = {"un":username,
            "width":2560,
            "height":1440,
            "hasRememberUn":True,
            "startURL":params['startURL'],
            "loginURL":"",
            "loginType":6,
            "useSecure":True,
            "local":"",
            "lt":"OAUTH",
            "qs":"r=https%3A%2F%2Flocalhost%3A8443%2Fsalesforce%2F21",
            "locale":"",
            "oauth_token":"",
            "oauth_callback":"",
            "login":"",
            "serverid":"",
            "display":"popup",
            "username":username,
            "pw":password,
            "Login":""}

    r2 = s.post("https://login.salesforce.com", data)
    m = re.search("window.location.href\s*='(.[^']+)'", r2.text)
    assert m is not None, "Couldn't find location.href expression in page %s (Username or password is wrong)" % r2.url

    u3 = "https://" +  urlparse.urlparse(r2.url).hostname + m.group(1)
    r3 = s.get(u3)

    m = re.search("window.location.href\s*='(.[^']+)'", r3.text)

    assert m is not None, "Couldn't find location.href expression in page %s:\n%s" % (r3.url, r3.text)

    return m.group(1)
