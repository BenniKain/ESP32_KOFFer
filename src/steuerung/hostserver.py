#!/usr/bin/env micropython
"""
MIT license
(C) Konstantin Belyalov 2017-2018
"""

import uasyncio as asyncio
import tinyweb

# Create web server application
app = tinyweb.webserver()


class POST_Method:
    data = []

    @classmethod
    def post(cls, data):
        print(data)
        cls.data.append(data)
        return redirect('/')
        return data


app.add_resource(POST_Method, url="/post")


# Index page
@app.route('/')
async def index(request, response):
    # Start HTTP response with content-type text/html
    await response.start_html()
    resp = ""
    with open("src/static/base.html", "r") as f:
        for line in f:
            resp += line
    # Send actual HTML page
    await response.send(resp)

# HTTP redirection
@app.route('/redirect')
async def redirect(request, response):
    # Start HTTP response with content-type text/html
    await response.redirect('/')


@app.route("/css/<fn>")
async def files_css(req, resp, fn):
    await resp.send_file(
        "src/static/{}".format(fn),
        content_type="text/css",
    )


@app.route("/js/<fn>")
async def files_js(req, resp, fn):
    await resp.send_file(
        "src/static/{}".format(fn),
        content_type="text/javascript",
    )


@app.route("/json/<fn>")
async def files_json(req, resp, fn):
    await resp.send_file(
        "src/static/configs/{}".format(fn),
        content_type="application/json", max_age=0,
    )

# for bootstrap css files
@app.route("/bootstrap/css/<fn>")
async def files_bootstrap_css(req, resp, fn):
    await resp.send_file(
        "src/static/bootstrap/css/{}.gz".format(fn),
        content_type="text/css",
        content_encoding="gzip"
    )


# for bootstrap js files
@app.route("/bootstrap/js/<fn>")
async def files_bootstrap_js(req, resp, fn):
    await resp.send_file(
        "src/static/bootstrap/js/{}.gz".format(fn),
        content_type="text/javascript",
        content_encoding="gzip",
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
