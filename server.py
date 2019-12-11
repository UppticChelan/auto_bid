from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

app = Flask(__name__)

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=os.environ.get('AUTH0_CLIENT_ID'),
    client_secret=os.environ.get('AUTH0_CLIENT_SECRET'),
    api_base_url='https:/os.environ.get('AWS_ACCESS_KEY_ID')/YOUR_DOMAIN',
    access_token_url='https://YOUR_DOMAIN/oauth/token',
    authorize_url='https://YOUR_DOMAIN/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)