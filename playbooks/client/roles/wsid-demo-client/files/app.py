from flask import Flask, jsonify, request, render_template
import os
import subprocess


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
                            
