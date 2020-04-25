consumer_key = 'ck_b51fb132ce35c050fe7da7adf73dc87e1cd3bf99'
consumer_secret = 'cs_04b94ae31616f8d07cf5306eaebdeb7898d24972'

import requests
import json

headers = {'Content-type': 'content_type_value'}
url = r"https://erasmus-stiftung.de/wp-json/gf/v2"
r = requests.get(url, headers=headers)
