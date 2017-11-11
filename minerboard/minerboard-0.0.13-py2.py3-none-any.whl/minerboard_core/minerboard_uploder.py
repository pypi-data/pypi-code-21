import configparser
import json
import time
import socket
from datetime import datetime

import os
import requests
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def config_read ():
    config = configparser.ConfigParser()
    config.sections()
    file = os.path.join(BASE_DIR,'config', 'config.ini')
    config.read(file)
    print(str(datetime.now()) + ' - Config have been read successfully')
    return config


def send_data(path, data):
    try:
        if path == '/login/':
            return requests.post('https://minerboard.pro/api' + path, json=data)
        elif path =='/report/':
            return requests.post('https://minerboard.pro/api' + path, json=data)
    except:
        print(str(datetime.now()) + ' - minerboard.pro is down')
        print('Script Closing in 10 sec')
        time.sleep(10)
        sys.exit()


def login(username,pwd):
    print(str(datetime.now()) + ' - Login to minerboard.pro')
    info = {'username': username, 'password': pwd}
    login_resp = send_data('/login/', info)
    result = login_resp.json()
    if result is not None:
        if result['status']:
            print(str(datetime.now()) + ' - Logged to minerboard.pro')
        else:
            print(str(datetime.now()) + ' - Login Failed')
            result = None
    return result


def nvidia_equihas_requst(nvidia_equihash, login_response, user, miner_name, address, port):
    if nvidia_equihash:
        print(str(datetime.now()) + ' - Request Data from Your Nvidia Equihash Miner')
        try:
            data = requests.get('http://' + address + ':' + port +'/getstat')
            recieved_data = data.json()
        except:
            print(str(datetime.now()) + " - Can't connect to Nvidia Zec miner Api")
            data = {'status': False, 'username': user, 'miner_name': miner_name, 'token': login_response['token'],
                    'miner': 'nvidia_equihash'}
            send_data('/report/', data)
            print('Script Closing in 10 sec')
            time.sleep(10)
            sys.exit()
        if login_response['status'] and recieved_data is not None:
            recieved_data['username'] = user
            recieved_data['miner_name'] = miner_name
            recieved_data['token'] = login_response['token']
            recieved_data['miner'] = 'nvidia_equihash'
            report = send_data('/report/', recieved_data)
            print(str(datetime.now()) + ' - Send Data from Your Nvidia Equihash to minerboard.pro')
            result = None
            try:
                result = report.json()
            except:
                print(result)
                print(str(datetime.now()) + ' - Bad server response contact minerboard.pro support')
            return result


def claymore_ethash(claymore_eth, login_response, user, miner_name,address, port):
    if claymore_eth:
        print(str(datetime.now()) + ' - Request Data from Your Ethash Miner')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((address, int(port)))
            sock.sendall(b'{"id":0, "jsonrpc":"2.0", "method":"miner_getstat1" }')
            recieved_data = json.loads(sock.recv(1024))
        except:
            print(str(datetime.now()) +  " - Can't connect to Eth miner Api")
            data = {'status': False, 'user': user, 'miner_name': miner_name, 'token': login_response['token'],
                    'miner': 'claymore_eth'}
            send_data('/report/',data)
            print('Script Closing in 10 sec')
            time.sleep(10)
            sys.exit()
        if login_response['status'] and recieved_data is not None:
            recieved_data['username'] = user
            recieved_data['miner_name'] = miner_name
            recieved_data['token'] = login_response['token']
            recieved_data['miner'] = 'claymore_eth'
            report = send_data('/report/', recieved_data)
            print(str(datetime.now()) + ' - Send Data from Your Ethash info to minerboard.pro')
            result = None
            try:
                result = report.json()
            except:
                print(str(datetime.now()) + ' - Bad server response contact minerboard.pro support')
            return result


def main():
    config = config_read()
    logged = login(config['Userinfo']['user'], config['Userinfo']['password'])
    if logged is not None and logged['status']:
        while True:
            if config['Algorithm']['nvidiaequihash'] == "True":
                result = nvidia_equihas_requst(config['Algorithm']['NvidiaEquihash'], logged, config['Userinfo']['user'],
                                               config['Userinfo']['minername'], config['ConectApiInfo']['address'],
                                               config['ConectApiInfo']['port_nvidia_zec'],
                                               )
            elif config['Algorithm']['ethash'] == "True":
                result = claymore_ethash(config['Algorithm']['Ethash'], logged, config['Userinfo']['user'],
                                         config['Userinfo']['minername'],config['ConectApiInfo']['address'],
                                         config['ConectApiInfo']['port_claymore_eth'],
                                         )
            else:
                print("All Algorithms set to False")
                result = None
            if config['Algorithm']['nvidiaequihash'] == "True" or config['Algorithm']['ethash'] == "True":
                if result is not None:
                   print(str(datetime.now()) + ' - Data have been sent successfully')
            time.sleep(int(config['CheckOptions']['requesttime']) * 60)


if __name__ == '__main__':
    main()
