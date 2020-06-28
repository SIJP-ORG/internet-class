import json
from flask import Flask, request, jsonify
import sqlite3
import datetime
from . import db

def test():
    return 'it works'

def sendnew():
    '''API to send a new message by the caller'''
    data = json.loads(request.data)
    ip = request.remote_addr
    hostname = "temp"
    arrival = datetime.datetime.now()
    body = data['msg']

    con = db.get_db()
    cur = con.cursor()
    cur.execute(
        'insert into msg (ip, hostname, arrival, body) values (?, ?, ?, ?)',
        (ip, hostname, arrival, body))
    rowid = cur.lastrowid
    con.commit()

    response = {'id': rowid, 'echo': data['msg']}
    return jsonify(response)

def getall():
    '''API to return all messages'''
    return jsonify(get_messages())

def get_messages():
    '''Internal method to retrieve the messages past 1 hour in.'''
    return db.get_db().execute(
        'select ip, hostname, arrival, body'
        ' from msg'
    ).fetchall()
