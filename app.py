#!/usr/bin/python
# -*- coding: utf-8 -*-
#    Copyright 2014 J. Fernando Sánchez Rada - Grupo de Sistemas Inteligentes
#                                                       DIT, UPM
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
'''
Example flask application that gets the most common words in review corpora
and show the reviews that contain those words.
'''
from flask import Flask, render_template, request
import clients
import config
import json
from clients import CorpusClient, LexiconClient

app = Flask(__name__)
app.debug = True

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/reviews')
@app.route('/reviews/<lang>')
@app.route('/reviews/<lang>/<domain>')
def reviews(lang="es", domain="hotel"):
    filterstring = request.args.get("filter", "").encode('utf-8')
    print("Lang {}, domain {}".format(lang,domain))
    c = CorpusClient(lang=lang, domain=domain, token=config.TOKEN)
    reviews = c.get_reviews(filter=filterstring)
    return json.dumps(reviews)

@app.route('/anchors')
@app.route('/anchors/<lang>')
@app.route('/anchors/<lang>/<domain>')
def anchors(lang="es", domain="hotel"):
    print("Lang {}, domain {}".format(lang,domain))
    c = CorpusClient(lang=lang, domain=domain, token=config.TOKEN)
    reviews = c.get_anchors()
    return json.dumps(reviews)

@app.route('/dictionary/<word>')
@app.route('/dictionary/<word>/<lang>')
def dictionary(word, lang="es"):
    c = LexiconClient(lang="es", domain="hotel", token=config.TOKEN)
    reviews = c.get_sentiments(word, lang)
    return json.dumps(reviews)


if __name__ == '__main__':
    app.run()
