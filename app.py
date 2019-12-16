
import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, Response, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from auto_bid import get_baselines, apply_bid_logic
import pandas as pd
import ruleset
import boto3
from botocore.client import Config
from io import StringIO
from functools import wraps
import json
from dotenv import load_dotenv, find_dotenv
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode
from datetime import date

today = date.today()

s3 = boto3.resource('s3', aws_access_key_id= os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),config=Config(signature_version='s3v4'))
ALLOWED_EXTENSIONS = {'csv'}
RULESET = os.path.dirname(os.path.abspath(__file__)) + 'ruless.csv'

app = Flask(__name__, static_url_path="/static")
app.secret_key = os.environ.get('SECRET_KEY_FLASK')

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=os.environ.get('AUTH0_CLIENT_ID'),
    client_secret=os.environ.get('AUTH0_CLIENT_SECRET'),
    api_base_url='https://dev-lxynygxp.auth0.com',
    access_token_url='https://dev-lxynygxp.auth0.com/oauth/token',
    authorize_url='https://dev-lxynygxp.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      return redirect('/login')
    return f(*args, **kwargs)

  return decorated

def get_client():
    return boto3.client(
        's3',
        'us-east-1',
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    )


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_to_bucket(df, channel, date, campaign):
    bucket = os.environ.get('S3_BUCKET')
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket, '{}{}{}.csv'.format(channel, date, campaign)).put(Body=csv_buffer.getvalue())

def run_autobid(df, new_rules):
    rules = ruleset.Ruleset()
    rules.makerules('ruless.csv')
    for rule in new_rules.keys():
        if rule in rules.rulesdict.keys():
            rules.rulesdict[rule] = new_rules[rule]
    rules.rules_update()
    group_cols = rules.groupby.split('|')

    df = ruleset.format_cols_input(df, rules)

    df['d7_total_revenue'] = df['D7 IAP Revenue'] + df['D7 Ad Revenue']
    baselines = df.groupby(group_cols).sum().reset_index()
    df['unadjusted_bid'] = df.apply(lambda x: ruleset.get_baselines(x['d7_total_revenue'], x['Installs'], rules), axis=1)
    baselines['base_bid'] = baselines.apply(lambda x: ruleset.get_baselines(x['d7_total_revenue'], x['Installs'], rules), axis=1)
    df = df.join(baselines[['Campaign Name', 'Country','base_bid']].set_index(['Campaign Name', 'Country']), on=['Campaign Name', 'Country'])
    if rules.method == 'hard cutoff':
        df['Bid'] = df.apply(lambda x: ruleset.apply_bid_logic(x['unadjusted_bid'], x['Installs'], x['base_bid'], rules), axis=1)
    else:
        df['Bid'] = df.apply(lambda x: ruleset.weighted_avg_bid(x['unadjusted_bid'], x['Installs'], x['base_bid'], rules), axis=1)
    df = df.round(2)
    campaign = df['Campaign Name'].iloc[0]
    channel = rules.output

    if channel == 'unity':
        df.sort_values(by='Campaign Name', axis=0, inplace=True)
        df.set_index(keys=['Campaign Name'], drop=False,inplace=True)
        names=df['Campaign Name'].unique().tolist()
        for name in names:
            name_frame = df.loc[df['Campaign Name']==name]
            name_frame = ruleset.format_cols_output(name_frame, rules)
            save_to_bucket(name_frame, channel, today, name)
    else:
        df = ruleset.format_cols_output(df, rules)
        save_to_bucket(df, channel, today, campaign)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            print('No file selected')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            df = pd.read_csv(file)
            new_rules = {}
            new_rules['input'] = request.form['input']
            new_rules['output'] = request.form['output']
            new_rules['method'] = request.form['method']
            if request.form['target']:
                new_rules['target'] = request.form['target']
            if request.form['max_bid_cap']:
                new_rules['max_bid_cap'] = request.form['max_bid_cap']
            print(new_rules)
            if request.form['min_bid_cap']:
                new_rules['min_bid_cap'] = request.form['min_bid_cap']
            if request.form['install_threshold']:
                new_rules['install_threshold'] = request.form['install_threshold']
            processed = run_autobid(df, new_rules)
            return redirect(url_for('download'))

    return render_template('index.html')

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=request.url_root + 'callback')

@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name']
    }
    return redirect('/download')

@app.route('/download', methods=['GET', 'POST'])
@requires_auth
def download():
    s3 = get_client()
    keys = []
    for obj in s3.list_objects_v2(Bucket=os.environ.get('S3_BUCKET'))['Contents']:
        keys.append(obj['Key'])
    if request.method == 'POST':
            file_name = (request.form['file_name'])
            file = s3.get_object(Bucket=os.environ.get('S3_BUCKET'), Key=file_name)
            return Response(
                file['Body'].read(),
                mimetype='text/plain',
                headers={"Content-Disposition": "attachment;filename={}.csv".format(file_name)}
            )
    else:
        return render_template('download.html', items=keys)



@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('login', _external=True), 'client_id': os.environ.get('AUTH0_CLIENT_ID')}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
