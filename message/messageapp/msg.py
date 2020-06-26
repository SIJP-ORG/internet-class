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

    con = db.get_db()
    cur = con.cursor()
    cur.execute(
        'insert into msg (sender, arrival, body) values (?, ?, ?)',
        (request.remote_addr, datetime.datetime.now(), data['msg'])
    )
    rowid = cur.lastrowid
    con.commit()

    response = {'id': rowid, 'echo': data['msg']}
    return jsonify(response)

def getall():
    '''API to return all messages'''
    msgs = db.get_db().execute(
        'select id, sender, arrival, body'
        ' from msg'
    ).fetchall()

    return jsonify(msgs)

def get_messages():
    '''Retrieve the latest 100 messages in reverse chronological order.'''
    return db.get_db().execute(
        'select sender, body'
        ' from msg'
    ).fetchall()
