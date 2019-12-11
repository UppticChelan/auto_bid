
import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, Response
from werkzeug.utils import secure_filename
from auto_bid import get_baselines, apply_bid_logic
import pandas as pd
import ruleset
import boto3
from botocore.client import Config
from io import StringIO

s3 = boto3.resource('s3', aws_access_key_id= os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),config=Config(signature_version='s3v4'))
ALLOWED_EXTENSIONS = {'csv'}
RULESET = os.path.dirname(os.path.abspath(__file__)) + 'ruless.csv'

app = Flask(__name__, static_url_path="/static")

def get_client():
    return boto3.client(
        's3',
        'us-east-1',
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request)
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
            if request.form['target']:
                new_rules['target'] = request.form['target']
            if request.form['max_bid_cap'] and request.form['max_bid_cap_bool'] is not True
                new_rules['max_bid_cap'] = request.form['max_bid_cap']
            if request.form['min_bid_cap']:
                new_rules['min_bid_cap'] = request.form['min_bid_cap']
            if request.form['install_threshold']:
                new_rules['install_threshold'] = request.form['install_threshold']
            processed = run_autobid(df, new_rules)
            return redirect(url_for('download'))

    return render_template('index.html')


def run_autobid(df, new_rules):
    rules = ruleset.Ruleset()
    rules.makerules('ruless.csv')
    if rule in new_rules.keys() in rules.rulesdict.keys():
        rules[rule] = new_rules[rule]
    group_cols = rules.groupby.split('|')

    df = format_cols_input(df, rules)

    df['d7_total_revenue'] = df['D7 IAP Revenue'] + df['D7 Ad Revenue']
    baselines = df.groupby(group_cols).sum().reset_index()
    df['unadjusted_bid'] = df.apply(lambda x: ruleset.get_baselines(x['d7_total_revenue'], x['Installs'], rules), axis=1)
    baselines['base_bid'] = baselines.apply(lambda x: ruleset.get_baselines(x['d7_total_revenue'], x['Installs'], rules), axis=1)
    df = df.join(baselines[['Campaign Name', 'Country','base_bid']].set_index(['Campaign Name', 'Country']), on=['Campaign Name', 'Country'])
    df['Bid'] = df.apply(lambda x: ruleset.apply_bid_logic(x['unadjusted_bid'], x['Installs'], x['base_bid'], rules), axis=1)
    df = df.round(2)

    df = format_cols_output(df, rules)

    bucket = os.environ.get('S3_BUCKET')
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket, 'df.csv').put(Body=csv_buffer.getvalue())

@app.route('/download')
def download():
    s3 = get_client()
    file = s3.get_object(Bucket=os.environ.get('S3_BUCKET'), Key='df.csv')
    return Response(
        file['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename=df.csv"}
    )



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
