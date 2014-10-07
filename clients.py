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
Wrappers around the EUROSENTIMENT APIs.
'''

from __future__ import print_function
import requests
import json
import logging

logger = logging.getLogger()

GET_REVIEWS = '''\
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#>
    PREFIX marl: <http://www.gsi.dit.upm.es/ontologies/marl/ns#>
    SELECT DISTINCT * from <{graph}>
    WHERE  {{ ?context a nif:Context .
             ?context nif:isString ?string .
             ?context marl:hasOpinion ?opinion .
             ?opinion marl:polarityValue ?polarityValue .
             ?opinion marl:hasPolarity ?polarity .
             FILTER (REGEX(?string, "{filter}"))}} LIMIT {limit}'''

DESCRIBE_OBJECT = '''\
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#>
    PREFIX marl: <http://www.gsi.dit.upm.es/ontologies/marl/ns#>
    SELECT DISTINCT ?property ?value from <{graph}>
    WHERE  {{ <{target}> ?property ?value. }} LIMIT {limit}'''

GET_ANCHORS = '''\
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#>
    PREFIX marl: <http://www.gsi.dit.upm.es/ontologies/marl/ns#>
    SELECT ?anchor ?category (count(?anchor) as ?count) from <{graph}>
    WHERE  {{ ?s nif:anchorOf ?anchor .
              ?s nif:posTag ?category .
              FILTER (?category IN ("NC", "ADJ", "ADV", "RB", "NN", "JJ"))
              FILTER(!str(?anchor) = "")
             }} ORDER BY desc(?count) LIMIT {limit}'''

GET_SENTIMENTS = '''\
            PREFIX lemon: <http://lemon-model.net/lemon#>
            PREFIX marl: <http://purl.org/marl/ns/>
            SELECT DISTINCT ?sense ?context ?polarityValue ?polarity from <{graph}>
            WHERE {{
                        ?sentimentEntry lemon:sense ?sense .
                        ?sense marl:polarityValue ?polarityValue .
                        ?sense marl:hasPolarity ?polarity .
                        ?sense lemon:reference ?reference .
                        ?sense lemon:context ?context .
                        ?entryWithSentiment lemon:sense ?context .
                        ?entryWithSentiment lemon:canonicalForm ?cf .
                        ?cf lemon:writtenRep "{word}"@{lang} .
            }} limit {limit}'''


CORPORA = {
    "es": {
        "hotel": "http://www.eurosentiment.eu/dataset/hotel/es/paradigma/0019/corpus",
        "electronics": "http://www.eurosentiment.eu/dataset/electronics/es/paradigma/0015/corpus"
    },
    "en": {
        "hotel": "http://www.eurosentiment.eu/dataset/electronics/en/paradigma/0014/corpus",
        "electronics": "http://www.eurosentiment.eu/dataset/hotel/en/paradigma/0018/corpus"
    }
}

LEXICA = {
    "es": {
        "hotel": "http://www.eurosentiment.eu/dataset/hotel/es/paradigma/0019/lexicon",
        "electronics": "http://www.eurosentiment.eu/dataset/electronics/es/paradigma/0015/lexicon"
    },
    "en": {
        "hotel": "http://www.eurosentiment.eu/dataset/electronics/en/paradigma/0014/lexicon",
        "electronics": "http://www.eurosentiment.eu/dataset/hotel/en/paradigma/0018/lexicon"
    }
}


class ResourceClient(object):

    def __init__(self,
                 token,
                 graph,
                 endpoint='http://54.201.101.125/sparql/'):
        self.graph = graph
        self.token = token
        self.endpoint = endpoint

    def request(self, input):
        headers = {"x-eurosentiment-token": self.token,
                   "content-type":"application/json"}
        data = {"query": input,
                "format": "application/json"}
        logger.debug("Query is {}".format(input))
        logger.debug("Endpoint is {}".format(self.endpoint))
        response = requests.post(self.endpoint,
                                 data=json.dumps(data),
                                 headers=headers)
        return json.loads(response.content)

    def get_objects(self, *args, **kwargs):
        response = self.request(*args, **kwargs)
        entries = []
        logger.debug("Response: ", response)
        for r in response["results"]["bindings"]:
            entries.append({key:r[key]["value"] for key in r })
        return entries

    def get_object(self, target, limit=100 ):
        response = self.request(DESCRIBE_OBJECT.format(graph=self.graph,
                                                       limit=limit,
                                                       target=target))
        a = {"@id": target}
        for r in response["results"]["bindings"]:
            key = r["property"]["value"]
            value = r["value"]["value"]
            if key in a:
                _temp = a[key]
                a[key] = [_temp, value]
            else:
                a[key] = value
        return a


class CorpusClient(ResourceClient):

    def __init__(self, token=None, lang="es", domain="hotel", **kwargs):
        super(CorpusClient, self).__init__(graph=CORPORA[lang][domain],
                                           token=token,
                                           **kwargs)

    def get_reviews(self, filter="", limit=100):
        results = self.get_objects(GET_REVIEWS.format(filter=filter,
                                                      graph=self.graph,
                                                      limit=limit))
        return results

    def get_anchors(self, limit=100):
        results = self.get_objects(GET_ANCHORS.format(graph=self.graph,
                                                      limit=limit))
        return results


class LexiconClient(ResourceClient):
    def __init__(self, token=None, lang="es", domain="hotel", **kwargs):
        super(LexiconClient, self).__init__(graph=LEXICA[lang][domain],
                                           token=token,
                                           **kwargs)

    def get_sentiments(self, word="",
                       lang="es",
                       graph=LEXICA["es"]["hotel"],
                       limit=100):
        results = self.get_objects(GET_SENTIMENTS.format(word=word,
                                                         graph=graph,
                                                         limit=limit,
                                                         lang=lang))
        return results


def test():
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    import config
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    c = CorpusClient(lang="en", domain="hotel", token=config.TOKEN)
    l = LexiconClient(config.TOKEN, "en", "hotel")
    anchors = c.get_anchors()
    logger.debug("Anchors")
    logger.debug(anchors)
    sentiments = l.get_sentiments(anchors[2]["anchor"])
    logger.debug("Sentiments")
    logger.debug(sentiments)
