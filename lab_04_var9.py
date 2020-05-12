# py_ver == "3.6.9"
import flask


app = flask.Flask(__name__)


import time
import logging


logging.basicConfig(filename="/var/log/secnotify/secnotify.log",
                    level=logging.DEBUG,
                    format='%(asctime)s:%(module)s:%(name)s:%(levelname)s:%(message)s')
logging.debug("secnotify startup")
logger = logging.getLogger()


@app.after_request
def after_request(response):
    timestamp = time.strftime('[%Y-%b-%d %H:%M]')
    app.logger.error(
                     '%s %s %s %s %s %s %s %s',
                                               timestamp,
                                               request.remote_addr,
                                               request.method,
                                               request.full_path,
                                               request.cookies,
                                               request.data,
                                               response.status,
                                               response.data
                    )
    return response


import json
import time


@app.route('/feedback_form')
def introduction():
    feedback = ''
    with open('feedback.json', 'r') as feedback_file:
        feedback_dict = json.loads(feedback_file.read())
        for key, value in feedback_dict.items():
            feedback += "<p><i>Анононим, %s</i>: %s</p>" % (key, value)
    return """<html>
                <title>Обратная связь</title>
                <body>
                %s
                    <form action="/save_feedback" method="post">
                        Поделитесь своим мнением: <input name="feedback" type="text" />
                        <input name="submit" type="submit" value="Отправить">
                    </form>
                </body>
            </html>
""" % feedback


@app.route('/save_feedback', methods=["GET", "POST"])
def index_page():
    feedback = flask.request.form.get('feedback')
    feedback_dict = {}
    with open('feedback.json', 'r') as feedback_file:
        feedback_dict.update(json.loads(feedback_file.read()))
    feedback_dict[time.time()] = feedback
    with open('feedback.json', 'w') as feedback_file:
        feedback_file.write(json.dumps(feedback_dict))
    return flask.redirect('/feedback_form')


@app.route('/send_host')
def set_target():
    return """
            <html>
                <title>Target selection</title>
                <body>
                    <form action="/scan">
                        Enter target IP: <input name="ip" type="text" />
                        <input name="submit" type="submit">
                    </form>
                </body>
            </html>
"""


import os


@app.route('/scan')
def scanner():
    ip = flask.request.args.get('ip')
    result = os.popen('nmap ' + ip).read()
    return "%s" % result


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Security-Policy'] = "default-src 'self'"
    return response


if __name__ == '__main__':
    app.run()
