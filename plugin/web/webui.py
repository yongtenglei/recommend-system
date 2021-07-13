#!/usr/bin/env python３
# -*- coding:utf-8 -*-
# author:mrpeng
# datetime:2021/2/5 下午1:58
import os
import logging

from plugin import REVIEWER, MySQL, Redis, item_config, user_behavior_config, hot_item_config, user_config


logging.getLogger("werkzeug").setLevel(logging.DEBUG)  # 不要删除
from flask_restful import Api

from plugin.utils import isValid, saveUserBehavior, saveHotItem, getItemInfo, \
    createUserBehavior
from flask import Flask, render_template, session, request, url_for, redirect
from plugin import log

__PWD = os.path.abspath(os.path.dirname(__file__))
__WEBIDE_PATH = os.path.join(__PWD, '..', '..', 'webIDE')
__WEBIDE_TEMPLATE_PATH = os.path.join(__WEBIDE_PATH, 'template')
__WEBIED_STATIC_PATH = os.path.join(__WEBIDE_PATH, 'static')
app = Flask("Recommend System", template_folder=__WEBIDE_TEMPLATE_PATH, static_folder=__WEBIED_STATIC_PATH)
app.config['SECRET_KEY'] = 'recommend system'
api = Api(app)

item_sql = MySQL(item_config, maxconnections=10)
user_behavior_sql = MySQL(user_behavior_config)
hot_item_handle = Redis(hot_item_config)
user_sql = MySQL(user_config)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route("/")
def root():
    login, userid = False, ''
    if 'userid' in session:
        login, userid = True, session['userid']
    return render_template('index.html', name="index", login=login, userid=userid)


@app.route("/search/<key>")
def search(key):
    login, userid = False, ''
    if 'userid' in session:
        login, userid = True, session['userid']
    return render_template('search.html', query_key=key, login=login, userid=userid)


@app.route("/item/<category>/<itemid>")
def itemInfo(category, itemid):
    login, userid = False, ''
    if 'userid' in session:
        login = True
        userid = session['userid']
        saveUserBehavior(user_behavior_sql, userid, itemid, category, REVIEWER)

    saveHotItem(hot_item_handle, category, itemid)
    item_info = getItemInfo(item_sql, itemid, category)
    return render_template("iteminfo.html", userid=userid, login=login, item=item_info)


@app.route("/login/", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        if isValid(user_sql, userid, password):
            session['userid'] = userid
            log.info("create User behavior table")
            createUserBehavior(user_behavior_sql, userid)
            log.info("create User success")
            return render_template('index.html', name="index", login=True, userid=userid)

    return render_template('login.html')


@app.route("/logout")
def logout():
    if 'userid' in session:
        userid = session['userid']
        if userid in hot_item_handle.connection.keys():
            hot_item_handle.set(userid, '')
    session.pop('userid', None)
    return redirect(url_for('root'))

from plugin.web.search import QuerySearch
from plugin.web.recommend import GuessYouLike
from plugin.web.recommend import Recommend
api = Api(app)
api.add_resource(QuerySearch, '/querysearch/<keyword>')
api.add_resource(GuessYouLike, '/guessyoulike')
api.add_resource(Recommend, '/recommend/<itemid>')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8002)
