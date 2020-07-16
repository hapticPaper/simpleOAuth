import requests
from flask import Flask, redirect, request, render_template, Response
import base64, time, random, urllib, os, json

app = Flask('Spotify Auth')

baseURL = "https://accounts.spotify.com"
CLIENT_ID = "9eb231ae8ee44d21a49c369a8e6409a7"
client_secret =  os.getenv('SPOTIFY_SECRET',"<INSERT YOUR SPOTIFY SECRET>")
B64AUTH = base64.b64encode(f"{CLIENT_ID}:{client_secret}".encode('utf8')).decode('utf8')
serving_domain = 'localhost'
PORT = 5000
REDIRECT_HOST = f"http://{serving_domain}:{PORT}/auth"
SPOTAPI = "https://api.spotify.com"


#Users will start here and we immediately check for an access token. Essentially they need it or theres nothing to do. 
@app.route('/')   
def start():
    return getAuthCode()

def getAuthCode():
    #This is called when we need to begin an oauth handshake. It requests the OAuth code and tells spotify who we are.
    # This data is returned back to us using the redirect_uri, we will use it for the next step.
    codeparams = urllib.parse.urlencode({
                'client_id':CLIENT_ID,
                'response_type':'code',
                'state': f"{random.random()}{time.time()}",
                'redirect_uri': f'{REDIRECT_HOST}'
        })
    return redirect(f"{baseURL}/authorize?{codeparams}")

@app.route('/auth')
def auth():
    #This is the second half of the OAuth handshake. With a uniqe code in hand (identifying the app) we can ask spotify 
    # to request access on behalf of the user. This is where the user is presented with a login screen. They will at-once
    # authenticate themselves and either grant or deny access.
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        token = requests.post(f"{baseURL}/api/token", 
                                data={'grant_type':'authorization_code',
                                    'code':code,
                                    'redirect_uri': f'{REDIRECT_HOST}'},
                                headers={'content_type':'application/x-www-form-urlencoded',
                                        'Authorization':f'Basic {B64AUTH}'})
        token=token.json()
       
        return me(token)
    except Exception as e:
        return e



@app.route('/refresh/<refresh_token>')
def refresh(refresh_token):
    token = requests.post(f"{baseURL}/api/token", 
                            data={'grant_type':'refresh_token',
                                  'refresh_token':refresh_token},
                            headers={'content_type':'application/x-www-form-urlencoded',
                                    'Authorization':f'Basic {B64AUTH}'})

    return token.json()



@app.route('/me')
def me(token=None):
    data = requests.get(f'{SPOTAPI}/v1/me',
                        headers = {'Authorization':f"Bearer {token['access_token']}"})
    return data.json()
        
if __name__ == '__main__':
    app.run(serving_domain,PORT ,debug=True)