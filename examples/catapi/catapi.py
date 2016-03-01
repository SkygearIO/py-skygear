# Copyright 2015 Oursky Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import skygear
import requests

from .feeder import pick_food

CATAPI_URL = 'http://thecatapi.com/api/images/get'


@skygear.op('catapi:get')
def get_cat():
    r = requests.get(CATAPI_URL, allow_redirects=False)
    if r.status_code == 302:
        return {'message': 'OK', 'url': r.headers['location']}
    else:
        return {'message': 'No cat for you!'}


@skygear.op('catapi:feed')
def feed(cat_name):
    return pick_food(cat_name)

