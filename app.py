
import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from auto_bid import get_baselines, apply_bid_logic
import pandas as pd
import ruleset
import boto3
from botocore.client import Config
from io import StringIO

s3 = boto3.resource('s3', aws_access_key_id= os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),config=Config(signature_version='s3v4')
ALLOWED_EXTENSIONS = {'csv'}
RULESET = os.path.dirname(os.path.abspath(__file__)) + 'ruless.csv'

app = Flask(__name__, static_url_path="/static")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            filename = secure_filename(file.filename)
            processed = process_file(filename)
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index.html')


def process_file(path, filename):
    #here is probably where to add update to channel
    run_autobid(path, filename)

def run_autobid(path, filename):
    df = pd.read_csv(path)
    rules = ruleset.Ruleset()
    rules.makerules('ruless.csv')
    group_cols = rules.groupby.split('|')
    df['d7_total_revenue'] = df['D7 IAP Revenue'] + df['D7 Ad Revenue']
    baselines = df.groupby(group_cols).sum().reset_index()
    df['unadjusted_bid'] = df.apply(lambda x: ruleset.get_baselines(x['d7_total_revenue'], x['Installs'], rules), axis=1)
    baselines['base_bid'] = baselines.apply(lambda x: ruleset.get_baselines(x['d7_total_revenue'], x['Installs'], rules), axis=1)
    df = df.join(baselines[['Campaign Name', 'Country','base_bid']].set_index(['Campaign Name', 'Country']), on=['Campaign Name', 'Country'])
    df['Bid'] = df.apply(lambda x: ruleset.apply_bid_logic(x['unadjusted_bid'], x['Installs'], x['base_bid'], rules), axis=1)
    df = df.round(2)
    ruleset.format_csv(df, rules, app.config['DOWNLOAD_FOLDER'], filename)
    s3.Bucket(os.environ.get('S3_BUCKET')).put_object(Key='file', Body=f, ContentEncoding='text/csv')

@app.route('/uploads/<filename>')
def uploaded_file():
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
