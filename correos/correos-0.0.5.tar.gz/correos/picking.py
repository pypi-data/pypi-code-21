#This file is part of correos. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from correos.api import API
from correos.utils import delivery_oficina

from stdnum import iban
from xml.dom.minidom import parseString
import os
import datetime
import genshi
import genshi.template

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


class Picking(API):
    """
    Picking API
    """
    __slots__ = ()

    def create(self, data):
        """
        Create delivery to Correos

        :param data: Dict
        :return: reference (str), label(base64), error (str)
        """
        reference = None
        label = None
        error = None

        tmpl = loader.load('picking_send.xml')
        services = delivery_oficina()
        CodProducto = data.get('CodProducto')

        vals = {
            'code': self.code,
            'now': datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            'Care': data.get('Care', '000000'),
            'TotalBultos': data.get('TotalBultos', '1'),
            'ModDevEtiqueta': data.get('ModDevEtiqueta', '2'),
            'RemitenteNombre': data.get('RemitenteNombre', '')[:50],
            'RemitenteApellido1': data.get('RemitenteApellido1', '')[:50],
            'RemitenteApellido2': data.get('RemitenteApellido2', '')[:50],
            'RemitenteNif': data.get('RemitenteNif', '')[:15],
            'RemitenteEmpresa': data.get('RemitenteEmpresa', '')[:50],
            'RemitentePersonaContacto': data.get('RemitentePersonaContacto', '')[:50],
            'RemitenteDireccion': data.get('RemitenteDireccion', '')[:50],
            'RemitenteNumero': data.get('RemitenteNumero', '')[:5],
            'RemitentePiso': data.get('RemitentePiso', '')[:5],
            'RemitentePuerta': data.get('RemitentePuerta', '')[:5],
            'RemitenteLocalidad': data.get('RemitenteLocalidad', '')[:50],
            'RemitenteProvincia': data.get('RemitenteProvincia', '')[:40],
            'RemitenteCP': data.get('RemitenteCP', '')[:5],
            'RemitenteTelefonocontacto': data.get('RemitenteTelefonocontacto', '')[:12],
            'RemitenteEmail': data.get('RemitenteEmail', '')[:50],
            'RemitenteNumeroSMS': data.get('RemitenteNumeroSMS', '')[:12],
            'RemitenteIdioma': data.get('RemitenteIdioma', '1'),
            'DestinatarioNombre': data.get('DestinatarioNombre', '')[:50],
            'DestinatarioApellido1': data.get('DestinatarioApellido1', '')[:50],
            'DestinatarioApellido2': data.get('DestinatarioApellido2', '')[:50],
            'DestinatarioDireccion': data.get('DestinatarioDireccion', '')[:50],
            'DestinatarioNumero': data.get('DestinatarioNumero', '')[:5],
            'DestinatarioPiso': data.get('DestinatarioPiso', '')[:5],
            'DestinatarioPuerta': data.get('DestinatarioPuerta', '')[:5],
            'DestinatarioLocalidad': data.get('DestinatarioLocalidad', '')[:50],
            'DestinatarioProvincia': data.get('DestinatarioProvincia', '')[:40],
            'DestinatarioCP': data.get('DestinatarioCP', '')[:5],
            'DestinatarioZIP': data.get('DestinatarioZIP', '')[:10],
            'DestinatarioPais': data.get('DestinatarioPais', ''),
            'DestinatarioTelefonocontacto': data.get('DestinatarioTelefonocontacto', '')[:12],
            'DestinatarioEmail': data.get('DestinatarioEmail', '')[:50],
            'DestinatarioNumeroSMS': data.get('DestinatarioNumeroSMS', '')[:12],
            'DestinatarioIdioma': data.get('DestinatarioIdioma', '1'),
            'CodProducto': CodProducto,
            'ReferenciaCliente': data.get('ReferenciaCliente', ''),
            'ReferenciaCliente2': data.get('ReferenciaCliente2', ''),
            'TipoFranqueo': data.get('TipoFranqueo', 'FP'),
            'TipoPeso': data.get('TipoPeso', 'R'),
            'Peso': data.get('Peso', '100'),
            'Largo': data.get('Largo', ''),
            'Alto': data.get('Alto', ''),
            'Ancho': data.get('Ancho', ''),
            'ImporteSeguro': data.get('ImporteSeguro', ''),
            'TipoReembolso': data.get('TipoReembolso', 'RC'),
            'Importe': data.get('Importe', ''),
            'NumeroCuenta': data.get('NumeroCuenta', ''),
            'EntregaExclusivaDestinatario': data.get('EntregaExclusivaDestinatario', 'N'),
            'Observaciones1': data.get('Observaciones1', '')[:45],
            'Observaciones2': data.get('Observaciones2', '')[:45],
            'InstruccionesDevolucion': data.get('InstruccionesDevolucion', 'D'),
            }

        if CodProducto in services:
            vals['ModalidadEntrega'] = services.get(CodProducto)
            if data.get('OficinaElegida'):
                vals['OficinaElegida'] = data.get('OficinaElegida')
            else:
                zip = data.get('DestinatarioCP')
                if not zip:
                    error = '%s: Add a delivery zip' % (data.get('ReferenciaCliente'))
                    return reference, label, error

                oficina = None
                for o in self.oficinas(zip):
                    if o['zip'] == zip:
                        oficina = o['code']
                        break
                if not oficina:
                    error = '%s: Can found a Oficina related with Zip %s' % (
                        data.get('ReferenciaCliente'),
                        zip,
                        )
                    return reference, label, error
                vals['OficinaElegida'] = oficina
        else:
            vals['ModalidadEntrega'] = 'ST'
            vals['OficinaElegida'] = None

        if data.get('Aduana'):
            vals['Aduana'] = True
            vals['AduanaTipoEnvio'] = data.get('AduanaTipoEnvio', '2')
            vals['AduanaEnvioComercial'] = data.get('AduanaEnvioComercial', 'S')
            vals['AduanaFacturaSuperiora500'] = data.get('AduanaFacturaSuperiora500', 'N')
            vals['AduanaDUAConCorreos'] = data.get('AduanaDUAConCorreos', 'N')
            vals['AduanaDescAduanera'] = data.get('AduanaDescAduanera', '')
            vals['AduanaFactura'] = data.get('AduanaFactura', 'S')
            vals['AduanaLicencia'] = data.get('AduanaLicencia', 'N')
            vals['AduanaCertificado'] = data.get('AduanaCertificado', 'N')
        else:
            vals['Aduana'] = False

        if not data.get('Largo'):
            vals['Largo'] = False
        if not data.get('Alto'):
            vals['Alto'] = False
        if not data.get('Ancho'):
            vals['Ancho'] = False

        if not data.get('ImporteSeguro'):
            vals['ImporteSeguro'] = False

        if not data.get('Reembolso'):
            vals['Reembolso'] = False
        else:
            vals['Reembolso'] = True
            # Spain delivery max price is 1000
            # TODO check price max other countries
            price = data.get('Importe')
            if not price or price > 1000:
                error = '%s: Price is None or larger than 1000' % (data.get('ReferenciaCliente'))
                return reference, label, error
            price = str(int(price * 100))
            vals['Importe'] = price.rjust(6, '0') # 900,50 = 090050
            # check if IBAN number or CC
            cc = data.get('NumeroCuenta')
            if not cc:
                error = '%s: Add a NumeroCuenta when is Reembolso' % (data.get('ReferenciaCliente'))
                return reference, label, error
            cc = iban.compact(cc)
            cc = iban.format(cc)
            if iban.is_valid(cc):
                vals['NumeroCuenta'] = iban.compact(cc[5:])
            else:
                vals['NumeroCuenta'] = iban.compact(cc)

        xml = tmpl.generate(**vals).render()
        result = self.connect(xml, 'Preregistro')
        if not result:
            return reference, label, error

        dom = parseString(result)

        Error = dom.getElementsByTagName('Error')
        if Error:
            code = Error[0].firstChild.data
            DescError = dom.getElementsByTagName('DescError')
            message = DescError[0].firstChild.data
            error = '%s: %s' % (code, message)
            return reference, label, error

        CodEnvio = dom.getElementsByTagName('CodEnvio')
        reference = CodEnvio[0].firstChild.data

        Resultado = dom.getElementsByTagName('Resultado')
        result = Resultado[0].firstChild.data

        if result == '1':
            error = 'Error send picking to Correos: "%s"' % (data.get('ReferenciaCliente'))

        #~ Etiqueta_pdf = dom.getElementsByTagName('Fichero')
        #~ NombreF = dom.getElementsByTagName('NombreF')
        Fichero = dom.getElementsByTagName('Fichero')
        label = Fichero[0].firstChild.data

        return reference, label, error

    def label(self, data):
        """
        Get PDF label from Correos service

        :param data: Dictionary of values
        :return: label (base64)
        """
        label = None

        tmpl = loader.load('picking_label.xml')

        vals = {
            'code': self.code,
            'now': datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            'Care': data.get('Care', '000000'),
            'ModDevEtiqueta': data.get('ModDevEtiqueta', '2'),
            'CodEnvio': data.get('CodEnvio', ''),
            }
        xml = tmpl.generate(**vals).render()
        result = self.connect(xml, 'SolicitudEtiquetaOp')
        if not result:
            return label

        dom = parseString(result)

        Fichero = dom.getElementsByTagName('Fichero')
        label = Fichero[0].firstChild.data

        return label
