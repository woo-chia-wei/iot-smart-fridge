import requests
from requests.auth import HTTPBasicAuth
import datetime

def check_qr_code (code):
    url = 'https://smart-fridge-ke.herokuapp.com/ingredient/status'
    user = 'iot'
    password = 'Ke123456@'
    query_params = {'qrcode': code}
    try:
        r = requests.get(url, params=query_params,
                         auth=HTTPBasicAuth(user, password), timeout=10).json()
        item_name = r['name']
        item_storied = r['status']
        return(item_name, item_storied)
    except requests.exceptions.RequestException as e:
        print(e)


def add_ingredient (sensor_data):
    url = 'https://smart-fridge-ke.herokuapp.com/ingredient/add'
    user = 'iot'
    password = 'Ke123456@'
    try:
        r = requests.post(url, data=sensor_data,
                          auth=HTTPBasicAuth(user, password), timeout=10)
    except requests.exceptions.RequestException as e:
        print(e)

def remove_ingredient (sensor_data):
    url = 'https://smart-fridge-ke.herokuapp.com/ingredient/delete'
    user = 'iot'
    password = 'Ke123456@'
    try:
        r = requests.post(url, data=sensor_data,
                          auth=HTTPBasicAuth(user, password), timeout=10)
    except requests.exceptions.RequestException as e:
        print(e)

def upload_sensor_data (sensor_data):
    url = 'https://smart-fridge-ke.herokuapp.com/sensorData/add'
    user = 'iot'
    password = 'Ke123456@'
    try:
        r = requests.post(url, data=sensor_data,
                          auth=HTTPBasicAuth(user, password), timeout=10)
    except requests.exceptions.RequestException as e:
        print(e)

