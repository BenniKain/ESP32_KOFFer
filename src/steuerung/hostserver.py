#!/usr/bin/env micropython
"""
MIT license
(C) Konstantin Belyalov 2017-2018
"""

import src.libraries.tinyweb as tinyweb
from src.steuerung.methoden import HTML_response

# Create web server application
app = tinyweb.webserver()

class POST_Method:

    @classmethod
    def post(cls, data):
        print(data)
        return data

app.add_resource(POST_Method,url="/button")


# Index page
@app.route('/')
async def index(request, response):
    # Start HTTP response with content-type text/html
    await response.start_html()
    h = HTML_response("src/html_css/base.html")
    table = h.build_table("Anzeige")
    resp = h.get_kwargs(table=table,command="Kommand")
    # Send actual HTML page
    await response.send(resp)

# HTTP redirection
@app.route('/redirect')
async def redirect(request, response):
    # Start HTTP response with content-type text/html
    await response.redirect('/')

@app.route("/espConfig")
async def espconfig(request,response):
    await response.start_html()
    h = HTML_response("src/html_css/base.html")
    table = h.build_table("ESPConfig")
    resp = h.get_kwargs(table=table,command="Kommand")
    # Send actual HTML page
    await response.send(resp)

@app.route("/buttontest")
async def buttontest(request, response):
    await response.start_html()
    h = HTML_response("src/html_css/base.html")
    table = "<a href=/button><button>einschalten</button></a>"
    resp = h.get_kwargs(table=table, command="Kommand")
    # Send actual HTML page
    await response.send(resp)

"<a href=\\button><button>einschalten</button></a>"
@app.route("/config")
async def config(request,response):
    await response.start_html()
    h = HTML_response("src/html_css/base.html")
    table = h.build_table("Config")
    resp = h.get_kwargs(table=table,command="Kommand")
    # Send actual HTML page
    await response.send(resp)
    


# Another one, more complicated page
@app.route('/ventilqueue')
async def ventilqueue(request, response):
    # Start HTTP response with content-type text/html
    await response.start_html()
    h = HTML_response("src/html_css/base.html")
    table = h.build_table("Ventilqueue")
    resp = h.get_kwargs(table=table,command="Kommand")
    await response.send(resp)

@app.route("/css/<fn>")
async def files_css(req, resp, fn):
    await resp.send_file(
        "src/html_css/{}".format(fn),
        content_type="text/css",
        )


async def run(host='0.0.0.0', loop_forever=True):
    app.run(host=host, port=8081, loop_forever=loop_forever)

def shutdown():
    app.shutdown()

if __name__ == '__main__':
    run()
    # To test your app:
    # - Terminal:
    #   $ curl http://localhost:8081
    #
    # - Browser:
    #   http://localhost:8081
    #   http://localhost:8081/table
    #
    # - To test HTTP redirection:
    #   curl http://localhost:8081/redirect -v
