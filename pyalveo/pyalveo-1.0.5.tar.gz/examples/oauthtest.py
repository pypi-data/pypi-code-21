import pyalveo
import webbrowser

if __name__=='__main__':

    oauth = {
        'client_id': 'b1692ca827a959f62a9b79e0eb471c9fdc3e818c33c976076f7948101ba23084',
        'client_secret': 'e533af5728a1334a089d9b446bda3204be4d59785734981832956b446cfbf64b',
        'redirect_url': 'https://10.126.98.204:4200/oauth/callback'
    }

    client = pyalveo.Client(api_url='https://staging.alveo.edu.au/', oauth=oauth, configfile='')

    print("Go to: ", client.oauth.get_authorisation_url())
    webbrowser.open(client.oauth.get_authorisation_url())


## https://10.126.109.47:4200/oauth/callback?code=3783c04cfe5123079250dfebe00d702fbd51266289247bf1d12593862b4dff44&state=PRmveN75QqLLDXeHH2ZuS6n0cNM6bQ+PRmveN75QqLLDXeHH2ZuS6n0cNM6bQ
