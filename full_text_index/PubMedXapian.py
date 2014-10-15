#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Christian Senger <der.senger@googlemail.com>
"""

import xappy
import sys
import os

from SynonymParser import SynonymParser
from Article import Article

class PubMedXapian():
    __indexCount  = 0
    __indexMsg    = ""

    def __init__(   self,
                    directory_name,
                    #no absolut path
                    xapianPath = "xapian",
                 ):
        self.__xapianPath   = os.path.join( xapianPath, directory_name )
        self.__pmids        = []
        self.__searchConn   = None 

    def __buildDoc(self, article):
        if article.getTitle() == None: return None
        
        doc = xappy.UnprocessedDocument()
        doc.fields.append(xappy.Field("title", article.getTitle()))
        if article.getAbstract() == None:
            pass
        else:
            doc.fields.append(xappy.Field("text", article.getAbstract()))
        
        #'INDEX_EXACT' - maximum length 220, but prefix "XA" is added to each term in the document 
        #maximum length 218
        for chemical in [chemical for chemical in article.getChemicals() if len(chemical) < 219]:
            doc.fields.append(xappy.Field("chemical_exact", chemical))

        for keyword in article.getKeywords():
            doc.fields.append(xappy.Field("keyword", keyword))

        for mesh in article.getMeSH():
            doc.fields.append(xappy.Field("mesh", mesh))

        doc.id = str(article.getPMID())
        return doc

    def buildIndexWithArticles(self, articles):
        conn = xappy.IndexerConnection(self.__xapianPath)

        #add priority to title field in case of ranked matching (weight=5)- index all fields and store data
        conn.add_field_action('title', xappy.FieldActions.INDEX_FREETEXT, weight=5, language='en')
        conn.add_field_action('text', xappy.FieldActions.INDEX_FREETEXT, language='en')
        conn.add_field_action('chemical_exact', xappy.FieldActions.INDEX_EXACT)
        conn.add_field_action('keyword', xappy.FieldActions.INDEX_FREETEXT, language='en')
        conn.add_field_action('mesh', xappy.FieldActions.INDEX_FREETEXT, language='en')

        conn.add_field_action('text', xappy.FieldActions.STORE_CONTENT)
        conn.add_field_action('title', xappy.FieldActions.STORE_CONTENT)
        conn.add_field_action('chemical_exact', xappy.FieldActions.STORE_CONTENT)
        conn.add_field_action('keyword', xappy.FieldActions.STORE_CONTENT)
        conn.add_field_action('mesh', xappy.FieldActions.STORE_CONTENT)

        for article in articles:
            doc = self.__buildDoc(article)
            if doc == None: continue
            try:
                #process doc to pdoc explicitly - not needed here
                #pdoc = conn.process(doc)
                conn.add(doc)
            except:
                continue

            PubMedXapian.__indexCount += 1
            nbs = len(PubMedXapian.__indexMsg)
            PubMedXapian.__indexMsg  = "article %s indexed" % (str(PubMedXapian.__indexCount))
            sys.stdout.write('\b' * nbs + PubMedXapian.__indexMsg)
        conn.flush()
        conn.close()

    def findPMIDsWithSynonyms(self, synonyms):
        if self.__searchConn == None:
            self.__searchConn = xappy.SearchConnection(self.__xapianPath)
            self.__searchConn.reopen()

        xapian_querys = []

        for querystring in synonyms:
            title, text, keyword, chemical_exact, mesh = '"' + querystring + '"', '"' + querystring + '"', '"' + querystring + '"', '"' + querystring + '"', '"' + querystring + '"'

            xapian_querys.append( self.__searchConn.query_field('title', title) )
            xapian_querys.append( self.__searchConn.query_field('text', text) )
            xapian_querys.append( self.__searchConn.query_field('keyword', keyword) )
            xapian_querys.append( self.__searchConn.query_field('chemical_exact', chemical_exact) )
            xapian_querys.append( self.__searchConn.query_field('mesh', mesh) )

        merged_q = self.__searchConn.query_composite(self.__searchConn.OP_OR, xapian_querys)
        results=self.__searchConn.search(merged_q, 0, self.__searchConn.get_doccount())

        return [r.id for r in results] 

