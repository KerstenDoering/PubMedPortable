#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2016, Kersten Doering <kersten.doering@gmail.com>

    This script creates a Lucene folder "lucene_index.Index" and adds two documents with the fields "Title" and "Abstract" from string variables.
"""

# lucene modules needed for this script
import lucene
from java.io import File
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.document import Document, Field, TextField

# start Java VM 
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# indexing directory
indexDir = FSDirectory.open(File("lucene_index.Index"))

# input which will be indexed with Lucene
title1 = "text of title1"
title2 = "title2"
abstract1 = "abstract1 has many words, e.g. hellow world can be the text"
abstract2 = "text of abstract2"

# configure indexing
config = IndexWriterConfig(Version.LUCENE_CURRENT, WhitespaceAnalyzer(Version.LUCENE_CURRENT))
config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
iw = IndexWriter(indexDir, config)

# count number of documents processed
nDocsAdded = 0

# create first document
doc = Document()
doc.add(TextField("Title", title1, Field.Store.YES))
doc.add(TextField("Abstract", abstract1, Field.Store.YES))
iw.addDocument(doc)
nDocsAdded += 1

# create second document
doc = Document()
doc.add(TextField("Title", title2, Field.Store.YES))
doc.add(TextField("Abstract", abstract2, Field.Store.YES))
nDocsAdded += 1

# add documents to Lucene index
iw.addDocument(doc)

# close IndexWriter
iw.close()

# show number of indexed documents
print "Indexed %d documents." % nDocsAdded


