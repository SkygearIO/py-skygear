import skygear
import requests


CATAPI_URL = 'http://thecatapi.com/api/images/get'


@skygear.op('catapi:get')
def get_cat():
    r = requests.get(CATAPI_URL, allow_redirects=False)
    if r.status_code == 302:
        return {'message': 'OK', 'url': r.headers['location']}
    else:
        return {'message': 'No cat for you!'}
