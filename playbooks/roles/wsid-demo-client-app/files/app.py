from flask import Flask, jsonify, request, render_template
import os
import subprocess
import requests
import logging
from paramiko.client import SSHClient, RejectPolicy
from paramiko.ed25519key import Ed25519Key
from io import StringIO
import tempfile 
from cachetools import cached, TTLCache

WSID_IDENTITY=os.getenv('WSID_IDENTITY') # https://thisdomain/<username>
WSID_DOMAIN=os.getenv("WSID_DOMAIN")
DEMO_UPSTREAM=os.getenv("DEMO_UPSTREAM")
DEMO_SSH_USER=os.getenv("DEMO_SSH_USER")
DEMO_DATA_DIR=os.getenv("DEMO_DATA_DIR")
WSID_ROTATION_MINUTES=os.getenv("WSID_ROTATION_MINUTES")
WSID_IDENTITY_FQDN="https://"+WSID_DOMAIN+"/.wsid/"+WSID_IDENTITY

#SECRET_SSH_KEY=Ed25519Key(file_obj=StringIO(SECRET_SSH_KEY_BODY))

CACHE_TTL=10
@cached(cache=TTLCache(maxsize=1,ttl=CACHE_TTL))
def get_secret_password():
    with open(f"{DEMO_DATA_DIR}/passwd", "r") as passwdfile:
        return passwdfile.read().decode()

app = Flask(__name__)

# TBD: move to core library
def load_remote_host_keys(host, hostkeys=None):
    logger = logging.getLogger('wsid')

    host_keys_endpoint = f"https://{host}/.wsid/ssh_host_ed25519_key.pub"
    logger.info(f"Fetching public keys from {host_keys_endpoint}")
   
    result =  requests.get(host_keys_endpoint)
    if not result.status_code==200:
        return 
    
    keys_body = result.text


    if hostkeys:
        for hostkey in keys_body.split("\n"):
            if not hostkey:
                continue
            logger.debug(f"Adding {host} {hostkey}")
            keytype,keybody=hostkey.split(" ")
            if keytype=='ssh-ed25519':
                hostkeys.add( host, keytype, Ed25519Key(data=keybody.encode()) )
    else:
        tfileobj, tfilepath=tempfile.mkstemp()
        logger.debug(f"Storing hostkeys to {tfilepath}: {keys_body}")
        os.write(tfileobj, keys_body.encode() )
        os.close(tfileobj)
        return tfilepath

class LogCapture(object):
    def __init__(self):
        self.messages = []

    def write(self, str):
        self.messages.append(str)

    def flush(self):
        pass

    def __str__(self):
        return "\n".join(self.messages)


def initialize_log_capturing(logger_names=None):
    capturer = LogCapture()
    handler = logging.StreamHandler(capturer)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
  
    if not logger_names:
        logger_names = [    
                        'wsid',
                        'paramiko',
                        'requests.packages.urllib3'
                       ]

    loggers = [ logging.getLogger(n) for n in logger_names ] 
    saved_levels = [ l.getEffectiveLevel() for l in loggers ]
    for logger in loggers:
        logger.addHandler(handler)    
        logger.setLevel(logging.DEBUG)

    log_remove_handler = lambda i: loggers[i].removeHandler(handler)
    log_restore_level  = lambda i: loggers[i].setLevel( saved_levels[i] )

    log_restore = lambda i: ( log_remove_handler(i), log_restore_level(i) )

    return (capturer, lambda: [ log_restore(i) for i in range(0, len(loggers) ) ])

@app.route("/")
def index():
    return render_template('index.html', 
                            upstream=DEMO_UPSTREAM, 
                            this_domain=WSID_DOMAIN, 
                            this_identity=WSID_IDENTITY,
                            demo_ssh_user=DEMO_SSH_USER,
                            wsid_rotation_minutes=WSID_ROTATION_MINUTES
                            )

@app.route("/test/http",methods=["POST"])
def test_http():

    capturer, log_teardown = initialize_log_capturing()
    logger=logging.getLogger('wsid')

    target_endpoint = f"https://{DEMO_UPSTREAM}/test/whoami"
    auth=(WSID_IDENTITY_FQDN, get_secret_password())

    logger.info(f"Testing server-to-server http call, API endpoint is {target_endpoint}, auth is {auth}")

    try:
        result=requests.post(target_endpoint, auth=auth)    
        logger.info(f"result: {result.status_code}, {result.text}")
    except Exception as e:
        logger.error(f"FAILURE: {e}")

    log_teardown()
    return jsonify(capturer.messages)

@app.route("/test/ssh", methods=["POST"])
def test_ssh():

    capturer, log_teardown = initialize_log_capturing()
    logger=logging.getLogger('wsid')
    
    ssh_endpoint=f"{DEMO_SSH_USER}@{DEMO_UPSTREAM}"

    logger.info(f"Testing SSH endpoint {ssh_endpoint} with temporary key")
    try:
        #with SSHClient() as ssh:
        #    hostkeys = ssh.get_host_keys()
            known_hosts_file = load_remote_host_keys(DEMO_UPSTREAM) #, hostkeys)

            cmdargs = ['ssh','-o',f'UserKnownHostsFile={known_hosts_file}',
                        '-i', f"{DEMO_DATA_DIR}/id_ed25519",
                        ssh_endpoint ]

            logger.info(f"Initiating connection as {cmdargs}")
 
            result = subprocess.run(cmdargs, shell=True, capture_output=True)
 
            logger.info(f"RESULT STDOUT: { result.stdout }")
            logger.info(f"RESULT STDERR: { result.stderr }")
        
            """
            ssh.connect(DEMO_UPSTREAM,
                        username=DEMO_SSH_USER,
                        look_for_keys=False,
                        allow_agent=False,
                        pkey=SECRET_SSH_KEY)


                    
            logger.info(f"Connection successful: {ssh._transport.get_banner()}")
            ssh.close()
            """

            os.unlink(known_hosts_file)

    except Exception as e:
        logger.exception(f"SSH FAILURE")
        
    log_teardown()
    return jsonify(capturer.messages)
