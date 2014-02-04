#!/usr/bin/env python2.7

from bottle import route, run, template, request, response

@route('/add')
def add_comment():
    data = request.query
    print("Adding comment for hash_id '%s'" % (data.hash_id))

@route('/get/<hash_id>')
def get_comments(hash_id):
    print("Fetching comments for '%s'" % (hash_id))
    response.headers['Content-Type'] = 'application/json'
    return("{ hash_id: 'ladida' }")

if __name__ == "__main__":
    run(host='localhost', port='8080')
