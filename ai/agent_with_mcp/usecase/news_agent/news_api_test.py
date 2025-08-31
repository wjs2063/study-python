import http.client, urllib.parse
import truststore
import json
from dotenv import load_dotenv
import os
load_dotenv()
truststore.inject_into_ssl()

from datetime import datetime,timedelta
api_token = os.getenv('THE_NEWS_API_TOKEN')
conn = http.client.HTTPSConnection('api.thenewsapi.com')

params = urllib.parse.urlencode({
    'api_token': api_token,
    #'categories': ", ".join(["경제","사회"]),
    'published_after' : (datetime.now() - timedelta(days=-7)).strftime("%Y-%m-%dT%H:%M:%S"),
    'search': "비트코인",
    'limit': 2,
})

conn.request('GET', '/v1/news/all?{}'.format(params))

res = conn.getresponse()
datas = res.read()
datas = json.loads(datas.decode('utf-8'))
print(type(datas),datas)
results = []
results.extend(
    [{"title": data["title"], "description": data["description"], "published_at": data["published_at"]} for data in
     datas["data"]])
print(results)