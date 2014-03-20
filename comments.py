#!/usr/bin/env python2.7
import sys, os
import datetime

# Make this run with Apache and mod_wsgi
if __name__ != "__main__":
    import site

    os.chdir(os.path.dirname(__file__))
    site.addsitedir(os.path.join(os.getcwd(), ".venv/lib/python2.7/site-packages"))

sys.path.append(os.getcwd())


from bottle import Bottle, HTTPResponse, route, run, template, request, response, default_app
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Sequence, String, DateTime, Text, desc
from sqlalchemy.ext.declarative import declarative_base
import json
import bleach

from wheezy.captcha.image import captcha

from wheezy.captcha.image import background
from wheezy.captcha.image import curve
from wheezy.captcha.image import noise
from wheezy.captcha.image import smooth
from wheezy.captcha.image import text

from wheezy.captcha.image import offset
from wheezy.captcha.image import rotate
from wheezy.captcha.image import warp

import config

Base = declarative_base()
engine = create_engine(config.DATABASE_URI, echo=config.DEBUG)

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
    article_id = Column(String(200))

    def __repr__(self):
        return "<Comment(user=%s, text=%s)>" % (self.username, self.text)

class Captcha(Base):
    __tablename__ = 'captcha'
    id = Column(Integer, Sequence('id_seq'), primary_key = True)
    value = Column(String(8))
    date_created = Column(DateTime(), default=datetime.datetime.now)

    def __repr__(self):
      return "<Captcha(id=%d, value=%s)>" % (self.id, self.value)

@app.post('/add')
def add_comment(db):
    username = request.forms.get('username')
    text = request.forms.get('text')
    article_id = request.forms.get('id')
    captcha_value = request.forms.get('captcha')
    captcha_id = request.forms.get('captcha_id')
    
    captcha = db.query(Captcha).get(captcha_id)
    captcha_ok = captcha_value.lower().strip() == captcha.value.lower()
    
    os.remove("captcha/captcha_%d.jpg" % (captcha.id))
    db.delete(captcha)

    if not captcha_ok:
        return json.dumps({"success": False})
    
    c = Comment(username=bleach.clean(username), text=bleach.clean(text), article_id=article_id)
    db.add(c)

    return json.dumps({"success": True})

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

@app.route('/captcha')
def create_captcha(db):
    import random
    import string

    value = random.sample(string.uppercase + string.digits, 5)
    c = Captcha(value=''.join(value))
    db.add(c)
    db.flush()

    img = captcha(drawings=[
                    background(color="#FFFFFF"),
                    text(fonts=[
                            "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf"
                         ],
                         font_sizes=[60],
                         squeeze_factor=1.0,
                         color="#50504f",
                         drawings=[
                            warp(),
                            #rotate(),
                            #offset()
                    ]),
                    curve(color='#40403f'),
                    #noise(),
                    #smooth()
                    ])

    finished_img = img(value)
    finished_img.save('captcha/captcha_%d.jpg' % (c.id), 'JPEG', quality=75)

    return json.dumps({ "id": c.id })

@app.route('/get_captcha/<id>')
def get_captcha(id, db):
    captcha = db.query(Captcha).get(id)
    if captcha.value:
        headers = {
            'Content-Type': 'image/jpeg'
        }

        with open("captcha/captcha_%d.jpg" % (captcha.id)) as stream:
            body = stream.read()

        return HTTPResponse(body, **headers)

def dt_converter(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime('%d.%m.%Y %H:%M:%S')
    else:
        return None

if __name__ == "__main__":
    app.run(host='localhost', port='8080')
else:
    application = app
