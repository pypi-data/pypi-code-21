'''
Created on 1 nov. 2017

@author: luisza
'''

import configparser
import os
import stat


class Institution:
    server_public_key=None
    public_certificate=None
    code=None
    private_key=None
    url_notify=None
    
class Settings(dict):
    
    TIMEZONE = 'America/Costa_Rica'
    ALGORITHM = 'sha512'
    DFVA_SERVER_URL = 'http://localhost:8000'
    AUTHENTICATE_INSTITUTION = '/authenticate/institution/'
    CHECK_AUTHENTICATE_INSTITUTION = '/authenticate/%s/institution_show/'
    SIGN_INSTUTION = '/sign/institution/'
    CHECK_SIGN_INSTITUTION = '/sign/%s/institution_show/'
    VALIDATE_CERTIFICATE = '/validate/institution_certificate/'
    VALIDATE_DOCUMENT = '/validate/institution_document/'
    SUSCRIPTOR_CONNECTED = '/validate/institution_suscriptor_connected/'

    SUPPORTED_SIGN_FORMAT = ['xml', 'odf', 'msoffice']
    SUPPORTED_VALIDATE_FORMAT = ['certificate', 'xml', 'odf', 'msoffice']

    SERVER_PUBLIC_KEY=''
    PUBLIC_CERTIFICATE=''
    CODE=''
    PRIVATE_KEY=''
    URL_NOTIFY='N/D'

    SETTINGS_LOADED=False
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.settings_file_path = os.path.join(
            os.environ.get('HOME'), ".dfva_python")
        self.settings_file_name = "client.conf"
        
        # If file not exists then create a config file
        if not os.path.exists( os.path.join(self.settings_file_path, self.settings_file_name) ):
            self.save()


    def get_institution(self):
        institution = Institution()
        institution.server_public_key=self.SERVER_PUBLIC_KEY
        institution.public_certificate=self.PUBLIC_CERTIFICATE
        institution.code=self.CODE
        institution.private_key=self.PRIVATE_KEY
        institution.url_notify=self.URL_NOTIFY
        
        return institution    
    
    def load_settings_from_file(self):
        self.SETTINGS_LOADED=True
        self.config.read(os.path.join(
            self.settings_file_path, self.settings_file_name))
        for section in self.config.sections():
            for key, value in self.config[section].items():
                key = key.upper()
                value = value.replace("@@", "%")
                try:
                    typ = type(getattr(self, key))
                    if typ == bool:
                        value = self.config.getboolean(section, key)
                    if typ == list:
                        value = value.split(",")
                    setattr(self, key, typ(value))
                except Exception as e:
                    pass
    def save(self):
        self.config['general']={
            'TIMEZONE' : self.TIMEZONE
        
        }

        self.config['DFVA'] = {
            'ALGORITHM': self.ALGORITHM,
            'DFVA_SERVER_URL' : self.DFVA_SERVER_URL,
            'AUTHENTICATE_INSTITUTION' : self.AUTHENTICATE_INSTITUTION,
            'CHECK_AUTHENTICATE_INSTITUTION': self.CHECK_AUTHENTICATE_INSTITUTION.replace("%", "@@"),
            'SIGN_INSTUTION': self.SIGN_INSTUTION,
            'CHECK_SIGN_INSTITUTION' : self.CHECK_SIGN_INSTITUTION.replace("%", "@@"),
            'VALIDATE_CERTIFICATE' : self.VALIDATE_CERTIFICATE,
            'VALIDATE_DOCUMENT': self.VALIDATE_DOCUMENT,
            'SUSCRIPTOR_CONNECTED': self.SUSCRIPTOR_CONNECTED,
            'SUPPORTED_SIGN_FORMAT': ",".join(self.SUPPORTED_SIGN_FORMAT),
            'SUPPORTED_VALIDATE_FORMAT' : ",".join(self.SUPPORTED_VALIDATE_FORMAT)   
            
        }
        
        self.config['institution']={
                'SERVER_PUBLIC_KEY': self.SERVER_PUBLIC_KEY,
                'PUBLIC_CERTIFICATE': self.PUBLIC_CERTIFICATE,
                'CODE': self.CODE,
                'PRIVATE_KEY': self.PRIVATE_KEY,
                'URL_NOTIFY': self.URL_NOTIFY
        }
        if not os.path.exists(self.settings_file_path):
            os.mkdir(self.settings_file_path)

        with open(os.path.join(self.settings_file_path, self.settings_file_name), "w") as configfile:
            self.config.write(configfile)
        os.chmod(os.path.join(self.settings_file_path, self.settings_file_name), stat.S_IRWXU)

    # This method above make settings to work as dict
    # but only accept attributes that are described in __init_()
    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def __setitem__(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(key)

    def __contains__(self, key):
        return hasattr(self, key)