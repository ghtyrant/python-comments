#!/usr/bin/env python2.7
import sys, os
import datetime

# Make this run with Apache and mod_wsgi
if __name__ != "__main__":
    import site

    os.chdir(os.path.dirname(__file__))
    site.addsitedir(os.path.join(os.getcwd(), ".venv/lib/python2.7/site-packages"))

sys.path.append(os.getcwd())


from bottle import Bottle, route, run, template, request, response, default_app
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Sequence, String, DateTime, Text, desc
from sqlalchemy.ext.declarative import declarative_base
import json
import bleach

import config

Base = declarative_base()
engine = create_engine(config.DATABASE_URI, echo=True)

app = Bottle()
plugin = sqlalchemy.Plugin(
            engine,
            Base.metadata,
            keyword='db',
            create=True,
            commit=True,
            use_kwargs=False
)

app.install(plugin)

class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, Sequence('id_seq'), primary_key = True)
    username = Column(String(100))
    date_posted = Column(DateTime(), default=datetime.datetime.now)
    text = Column(Text())
    article_id = Column(String(10))

    def __repr__(self):
        return "<Comment(user=%s, text=%s)>" % (self.username, self.text)

@app.post('/add')
def add_comment(db):
    username = request.forms.get('username')
    text = request.forms.get('text')
    article_id = request.forms.get('id')

    c = Comment(username=bleach.clean(username), text=bleach.clean(text), article_id=article_id)
    db.add(c)
    return "{ success: true }"

@app.route('/get/<hash_id>')
def get_comments(hash_id, db):
    # only accept XHR reques
    if not config.DEBUG and not request.is_xhr:
        return

    comments = []
    for comment in db.query(Comment).filter_by(article_id = hash_id).order_by(desc(Comment.date_posted)):
        comments.append({ 'username': comment.username, 'text': comment.text, 'date_posted': comment.date_posted })

    response.headers['Content-Type'] = 'application/json'
    return(json.dumps({ 'comments': comments }, default=dt_converter))

@app.route('/count/<hash_id>')
def count_comments(hash_id, db):
    # only accept XHR reques
    if not config.DEBUG and not request.is_xhr:
        return

    comment_count = db.query(Comment).filter_by(article_id = hash_id).count()

    response.headers['Content-Type'] = 'application/json'
    return(json.dumps({ 'count': comment_count }))


def dt_converter(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime('%d.%m.%Y %H:%M:%S')
    else:
        return None

if __name__ == "__main__":
    app.run(host='localhost', port='8080')
else:
    application = app
