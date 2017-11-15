#This file is part of correos. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

def correos_url(debug=False):
    """
    Correos URL connection

    :param debug: If set to true, use Envialia test URL
    """
    if debug:
        return 'https://preregistroenviospre.correos.es/preregistroenvios'
    else:
        return 'https://preregistroenvios.correos.es/preregistroenvios'
        
def services():
    services = {
        'S0030': 'PAQUETE POSTAL PRIORITARIO (I)',
        'S0033': 'POSTAL EXPRES (N)',
        'S0034': 'POSTAL EXPRES (I)',
        'S0198': 'POSTAL EXPRES LISTA',
        'S0132': 'PAQ 72 DOMICILIO',
        'S0133': 'PAQ 72 OFICINA',
        'S0135': 'LOGISTICA INVERSA CON ENVIO ASOCIADO',
        'S0148': 'LOGISTICA INVERSA DE RETORNO',
        'S0235': 'PAQ 48 ENTREGA A DOMICILIO',
        'S0236': 'PAQ 48 EN OFICINA',
        'S0197': 'PAQ 48 (LOGISTICA INVERSA)',
        'S0031': 'PAQUETE POSTAL ECONOMICO (I)',
        'S0175': 'PAQ 48 ENTREGA EN HOMEPAQ',
        'S0176': 'PAQ 48 ENTREGA EN CITYPAQ',
        'S0177': 'PAQ 72 ENTREGA EN HOMEPAQ',
        'S0178': 'PAQ 72 ENTREGA EN CITYPAQ',
    }
    return services

def delivery_oficina():
    services = {
        'S0236': 'LS',
        'S0133': 'LS',
        }
    return services
