#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2016, Kersten Doering <kersten.doering@gmail.com>

    This script reads the Lucene index "lucene_index.Index". It builds one query over Title and Abstract field with "OR" and one query with "AND".
"""

# lucene modules needed for this scriptimport lucene
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.search import IndexSearcher

# start Java VM 
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# configure search parameters
directory = SimpleFSDirectory(File("lucene_index.Index"))
searcher = IndexSearcher(DirectoryReader.open(directory))
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

# query term
term = "text"

# first query using OR
print "Searching for '" + term + "' with OR two match both documents:"
query = QueryParser(Version.LUCENE_CURRENT, "Title", analyzer).parse("(Title:" + term + ") OR (Abstract:" + term + ")" )#+ " AND Abstract:" + command)
# get results
results = searcher.search(query, 50).scoreDocs
print "%s total matching documents." % len(results)
# show results
for result in results:
    doc = searcher.doc(result.doc)
    print 'title:', doc.get("Title"), ', abstract:', doc.get("Abstract")

# second query using AND
print "\n\nSearching for '" + term + "' with OR two match only the first document:"
query = QueryParser(Version.LUCENE_CURRENT, "Title", analyzer).parse("(Title:" + term + ") AND (Abstract:" + term + ")" )#+ " AND Abstract:" + command)
# get results
results = searcher.search(query, 50).scoreDocs
print "%s total matching documents." % len(results)
# show results
for result in results:
    doc = searcher.doc(result.doc)
    print 'title:', doc.get("Title"), ', abstract:', doc.get("Abstract")
