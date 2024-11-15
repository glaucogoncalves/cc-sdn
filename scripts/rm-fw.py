import requests

# REST API url and headers
host = "<IP-PUBLICO-DA-EC2>"
port = "8181"
username = "onos"
password = "rocks"
url = f"http://{host}:{port}/onos/v1/acl/rules"

# remove all rules from the ACL using the REST API
resp = requests.delete(url, auth=(username, password))
print(resp.text)