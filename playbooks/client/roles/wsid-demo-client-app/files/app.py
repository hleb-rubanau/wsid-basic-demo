from flask import Flask, jsonify, request, render_template
import os
import subprocess
import requests
from paramiko.client import SSHClient, RejectPolicy
from paramiko.ed25519key import Ed25519Key
from io import StringIO

WSID_IDENTITY=os.getenv('WSID_IDENTITY') # https://thisdomain/<username>
WSID_DOMAIN=os.getenv("WSID_DOMAIN")
DEMO_UPSTREAM=os.getenv("DEMO_UPSTREAM")
DEMO_SSH_USER=os.getenv("DEMO_SSH_USER")
WSID_IDENTITY_FQDN="https://"+WSID_DOMAIN+"/.wsid/"+WSID_IDENTITY

# injects SECRET_PASSWORD and SECRET_SSH_KEY_BODY
with open('./secrets.py','r') as secretsfile:
    exec(compile(secretsfile.read(), './secrets.py','exec') )

SECRET_SSH_KEY=Ed25519Key(file_obj=StringIO(SECRET_SSH_KEY_BODY))

app = Flask(__name__)

# TBD: move to core library
def load_remote_host_keys(host, hostkeys):
    logging.getLogger('wsid')

    host_keys_endpoint = "https://{host}/.wsid/ssh_host_ed25519.pub"
    logger.info("Fetching public keys from {host_keys_endpoint")
    
    keys_body = requests.get(host_keys_endpoint).text
    for hostkey in keys_body.split("\n"):
        if not hostkey:
            continue
        logger.debug(f"Adding {host} {hostkey}")
        keytype,keybody=hostkey.split(" ")
        hostkeys.add( host, keytype, keybody )



class LogCapture(object):
    def __init__(self):
        self.messages = []

    def write(self, str):
        self.messages.append(str)

    def flush(self):
        pass

    def __str__(self):
        return "\n".join(self.messages)


def initialize_log_capturer(logger):
    capturer = LogCapture()
    handler = logging.StreamHandler(capturer)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
  
    logger=logging.getLogger() 
    logger.addHandler(handler)

    return (capturer, lambda x: logger.removeHandler(handler))

@app.route("/")
def index():
    return render_template('index.html', 
                            upstream=DEMO_UPSTREAM, 
                            this_domain=WSID_DOMAIN, 
                            this_identity=WSID_IDENTITY)

@app.route("/test/http",methods=["POST"])
def test_http():

    logger=logging.getLogger()
    capturer, log_teardown = initialize_log_capturer( logger )

    target_endpoint = f"https://{DEMO_UPSTREAM}/test/whoami"
    auth=(WSID_IDENTITY_FQDN, SECRET_PASSWORD)              

    logger.info(f"Testing server-to-server http call, API endpoint is {target_endpoint}, auth is {auth}")

    try:
        result=requests.post(target_endpoint, auth=auth)    
        logger.info(f"result: {result.status_code}, {result.text}")
    except e:
        logger.error(f"FAILURE: {e}")

    log_teardown()
    return jsonify(capturer.messages)

@app.route("/test/ssh", methods=["POST"])
def test_ssh():
    logger=logging.getLogger('wsid')
    capturer, log_teardown = initialize_log_capturer( logger )
    
    ssh_endpoint=f"{DEMO_SSH_USER}@{DEMO_UPSTEAM}"

    logger.info(f"Testing SSH endpoint {ssh_endpoint} with temporary key")
    try:
        with SSHClient() as ssh:
            hostkeys = ssh.get_host_keys()
            load_remote_host_keys(DEMO_UPSTREAM, hostkeys)

            logger.info("Initiating connection")

            ssh.connect(DEMO_UPSTREAM,
                        username=DEMO_SSH_USER,
                        look_for_keys=False,
                        allow_agent=False,
                        pkey=SECRET_SSH_KEY)


                    
            logger.info(f"Connection successful: {ssh._transport.get_banner()}")
            ssh.close()
    except e:
        logger.error(f"FAILURE: {e}")
        
    log_teardown()
    return jsonify(messages)
