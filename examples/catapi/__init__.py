from .catapi import *

from skygear import static_assets
from skygear.utils.assets import directory_assets


@static_assets('hello')
def hello_world():
    return directory_assets('files')
