# Test Salesforce oauth login
import os.path
import pickle

import salesforce_oauth_request

if os.path.exists("test_settings"):
	creds = pickle.loads(open("test_settings").read())
	client_id = creds['client_id']
	client_secret = creds['client_secret']
	redirect_uri = creds['redirect_uri']
else:
	client_id = raw_input("Oauth Client ID: ")
	client_secret= raw_input("Oauth Client Secret: ")
	redirect_uri = raw_input("Redirect URI: ")
	with open("test_settings", "w") as f:
		f.write(pickle.dumps(dict(client_id=client_id, 
								  client_secret=client_secret, 
								  redirect_uri=redirect_uri)))

username = raw_input("Username: ")
password = raw_input("Password: ")

print "............."
packet = salesforce_oauth_request.login(username=username,
										password=password,
										client_id=client_id,
										client_secret=client_secret,
										redirect_uri=redirect_uri
										)

print "Access token: %s" % packet['access_token']
print "Refresh token: %s" % packet['refresh_token']
print "Instance URL: %s" % packet['instance_url']

# print salesforce_oauth_request.login(
# 	username="scottp@mobileforce.com",
# 	password="rocket14",
# 	client_id="3MVG9rFJvQRVOvk7dcW8zRXD4lv7ZdT638O2Ti7hrGGo2Oa7iFCoyabLryNhGv_j2x9yo0Ea6.VmqzUR6LDgD",
# 	client_secret="7176140918132069100",
# 	redirect_uri="https://localhost:8443/oauth/code"
# 	)