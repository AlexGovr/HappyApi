import requests


def many(s, e):
    return [
        {'order_id':_id,
        'region':4,
        'weight': 12,
        'delivery_hours':['10:00-12:00', '13:00-14:00']}
        for _id in range(s, e+1)]
s = 30

json_post={
    'data':[
        {'weight': 12,
        'order_id': s+2,
        'region':4,
        'delivery_hours':['10:00-12:00', '13:00-14:00']}
    ]
}
json_post['data'] += many(s, s+1)

# POST
urll_post = 'http://127.0.0.1:8000/orders'
urls_post = 'http://178.154.195.226/orders'

# GET
urll_get = 'http://127.0.0.1:8000/orders'
urls_get = 'http://178.154.195.226/orders'

req = requests.post
url_to_use = 'local'


if req == requests.get:
    url = urls_get
    if url_to_use == 'local':
        url = urll_get
    r = req(url, json=json_post)
    print(r.status_code, r.reason, r.text)

if req == requests.post:
    url = urls_post
    if url_to_use == 'local':
        url = urll_post
    r = req(url, json=json_post)
    print(r.status_code, r.reason, r.text)
    