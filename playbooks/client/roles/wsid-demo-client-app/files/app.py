from flask import Flask, jsonify, request, render_template
import os
import subprocess
import requests
from paramiko.client import SSHClient, RejectPolicy

PASSWORD_FILE_LOCATION=os.getenv("WSID_PASSWD_FILE")
KEY_FILE_LOCATION=os.getenv("WSID_KEY_FILE")
WSID_IDENTITY=os.getenv('WSID_IDENTITY') # https://thisdomain/<username>
DEMO_UPSTREAM=os.getenv("DEMO_UPSTREAM")
DEMO_SSH_USER=os.getenv("DEMO_SSH_USER")


# to be re-read on reload and NOT exposed as ENV vars
with open(PASSWORD_FILE_LOCATION,'r') as pwdfile:
    SECRET_PASSWORD=pwdfile.read().strip()
with open(KEY_FILE_LOCATION,'r') as keyfile:
    SECRET_KEYFILE=keyfile.read().strip()


app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html', 
                            upstream=DEMO_UPSTREAM)

@app.route("/test/http",methods=["POST"])
def test_http():

    target_endpoint = f"https://{DEMO_UPSTREAM}/test/whoami"
    auth=(WSID_IDENTITY, SECRET_PASSWORD)              

    messages = [ f"Testing server-to-server http call, API endpoint is {target_endpoint}, auth is {auth}"   ] 
    try:
        result=requests.post(target_endpoint, auth=auth)    
        messages.append( f"result: {result.status_code}, {result.text}" )
    except e:
        messages.append(f"FAILURE: {e}")

    return jsonify(messages)

@app.route("/test/ssh", methods=["POST"])
def test_ssh():
    ssh_endpoint=f"{DEMO_SSH_USER}@{DEMO_UPSTEAM}"

    host_keys_endpoint = "https://{DEMO_UPSTREAM}/.ssh/ssh_host_keys"
    messages = [ f"Testing SSH endpoint {ssh_endpoint} with temporary key" ]
    try:
        messages.append(f"Fetching ssh host keys from {host_keys_endpoint} (could be cached)...")
        keys_body = requests.get(host_keys_endpoint).text

        messages.append(f"Trying to SSH to f{ssh_endpoint}..."
       
        ssh = SSHClient() 
    
    except e:
        messages.append(f"FAILURE: {e}")
        

    return jsonify(messages)
