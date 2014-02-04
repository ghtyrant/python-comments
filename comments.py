#!/usr/bin/env python2.7

# Make this run with Apache and mod_wsgi
if __name__ != "__main__":
    import os
    import site

    os.chdir(os.path.dirname(__file__))
    site.addsitedir(os.path.join(os.getcwd(), ".venv/lib/python2.7/site-packages"))


from bottle import route, run, template, request, response, default_app
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base

import config

Base = declarative_base()
engine = create_engine(DATABASE_URI)

app = bottle.Bottle()
plugin = sqlalchemy.Plugin(
            engine,
            Base.metadata,
            keyword='db',
            create=True,
            commit=True,
            use_kwargs=False
)

app.install(plugin)

@app.post('/add')
def add_comment(db):
    data = request.query
    print("Adding comment for hash_id '%s'" % (data.hash_id))

@app.get('/get/<hash_id>')
def get_comments(hash_id, db):
    # only accept XHR request
    if not request.is_xhr:
        return

    print("Fetching comments for '%s'" % (hash_id))
    response.headers['Content-Type'] = 'application/json'
    return("{ hash_id: 'ladida' }")

if __name__ == "__main__":
    run(host='localhost', port='8080')
else:
    application = app
