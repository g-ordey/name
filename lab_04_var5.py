# py_ver == "3.6.9"
import flask


app = flask.Flask(__name__)


# root_ssh_pwd = "k33pc41mU$$Ri$c0min9"
# main_server_ip = "8.8.8.8"


@app.route("/")
def MainPage():
    return """
            <html>
            <body>
            <script>
            url = new URL(window.location.href);
            var parameter = url.searchParams.get("name");
            hello = "<h1>Hello, " + parameter + "</h1>";
            document.write(hello);
            </script>
            </body>
            </html>
            """


import requests
@app.route('/parser', methods=['GET', 'POST'])
def parse_list():
    if flask.request.method == 'POST':
        if 'file' not in flask.request.files:
            return flask.redirect(flask.request.url)
        file = flask.request.files['file']
        if file.filename == '':
            return flask.redirect(flask.request.url)
        if file and file.filename.endswith(".xml"):
            from xml.dom import pulldom
            parser = pulldom.parse(file)
            for node in parser:
                data = node[1]
                parser.expandNode(data)
                requests.post("https://storage.mainfraim.ecc/save_data", data=data.toxml())
    return flask.redirect('/load_xml')


@app.route('/load_xml')
def loader():
    return """
    <html>
      <body>
        <h2>Загрузите XML-документ для обработки</h2>
        <form action="/parser" method="post" enctype="multipart/form-data">
          <input name="file" type="file">
          <input name="submit" type="submit" value="Загрузить">
        </form>
      </body>
    </html>
    """


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Security-Policy'] = "default-src 'self'"
    return response


if __name__ == '__main__':
    app.run()
