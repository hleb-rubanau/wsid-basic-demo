from flask import Flask, jsonify, request, render_template
import logging

app = Flask(__name__)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger("gunicorn.error")
    root_logger=logging.getLogger()
    root_logger.handlers = gunicorn_logger.handlers
    root_logger.setLevel(gunicorn_logger.level)


@app.route('/test/whoami', methods=["POST"])
def whoami():
    return jsonify( {
                        'status': 'success',
                        'identity': request.headers.get('X-WSID-Identity') 
                        #, 'headers': dict(request.headers)
                    } )
