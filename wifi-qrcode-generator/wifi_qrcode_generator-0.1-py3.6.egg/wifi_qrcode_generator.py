"""Generate a QR code to make it easy for other people to connect to the wifi
network.
"""

import qrcode
import getpass


def wifi_qrcode(ssid, hidden, authentication_type, password=None):
    """Generate Wifi QR code for given parameters
    Parameters
    ----------
    ssid: str
         SSID
    hidden: bool
         Specify if the network is hidden
    authentication_type: str
         Specify the authentication type. Supported types: WPA, WEP, nopass
    password: str
         Password. Not required if authentication type is nopass
    """

    if authentication_type in ['WPA', 'WEP'] and password is not None:
        qr = qrcode.make(
            f'WIFI:T:{authentication_type};S:{ssid};P:{password};H:'
            f'{str(hidden).lower()};;')
    elif type == "nopass":
        qr = qrcode.make(
            f'WIFI:T:{authentication_type};S:{ssid};H:{str(hidden).lower()};;')
    else:
        print(ssid, hidden, authentication_type, password)
        raise TypeError("Invalid parameters")
    return qr.get_image()


def main():
    while True:
        ssid = input("SSID: ")
        if ssid == "":
            print("Input is not valid!")
        else:
            break

    while True:
        hidden = input("Is the network hidden (default is false): ").lower()
        if hidden in ['yes', 'y', 'true', 't']:
            hidden = True
            break
        elif hidden in ['', 'no', 'n', 'false', 'f']:
            hidden = False
            break
        else:
            print("Input is not valid!")
    
    while True:
        print("Authentication types: WPA/WPA2, WEP, nopass")
        authentication_type = input("Authentication type (default is "
                                    "WPA/WPA2): ").lower()
        if authentication_type in ['', 'wpa2', 'wpa', 'wpa/wpa2', 'wpa2/wpa']:
            authentication_type = 'WPA'
            break
        elif authentication_type == 'WEP' or authentication_type == 'nopass':
            break
        else:
            print("Input is not valid!")
    
    while True:
        if authentication_type == 'nopass':
            password = None
            break    
        password = getpass.getpass("Password: ")
        if password == "":
            print("Input not valid!")
        else:
            break
    qrcode = wifi_qrcode(ssid, hidden, authentication_type, password)
    qrcode.save(ssid+'.png')
    print("The qr code has been stored in the current directory.")

if __name__ == '__main__':
    main()
