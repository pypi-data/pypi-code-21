'''
Created on 2 nov. 2017

@author: luisza
'''


from dfva_python.client import Client
c = Client()
auth_resp = c.authenticate('04-0212-0119')
print(auth_resp)
c.check_autenticate(auth_resp['id_transaction'])


DOCUMENT = '''IyEvYmluL2Jhc2gKCk5PRk9SQ0U9dHJ1ZQpBUFRfQ0FDSEU9IiIKCndoaWxlIGdldG9wdHMgY2h5
IG9wdGlvbgpkbwogY2FzZSAiJHtvcHRpb259IgogaW4KIHkpIE5PRk9SQ0U9ZmFsc2U7OwogYykg
QVBUX0NBQ0hFPXRydWU7OwogaCkgbXloZWxwCiAgICBleGl0IDAgOzsKIGVzYWMKZG9uZQoKaWYg
WyAkQVBUX0NBQ0hFIF07IHRoZW4gCiBlY2hvICJCSU5HTyIgCmZpCgo='''

sign_resp=c.sign( '04-0212-0119', DOCUMENT.encode(), "resumen ejemplo", _format='xml')
print(sign_resp)
c.check_sign(sign_resp['id_transaction'])

c.validate(DOCUMENT, 'certificate')
c.validate(DOCUMENT, 'xml')
c.is_suscriptor_connected('04-0212-0119')