#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script reads annotations from a given XML document in BioC format and prints them to command-line.
"""

# PyBioC API
from bioc import BioCReader

# open BioC XML file and DTD file with XML structure definitions
bioc_reader = BioCReader("text_PubTator.xml", dtd_valid_file="BioC.dtd")
# read files
bioc_reader.read()
# get documents from BioC XML file (PubMed abstracts)
docs = bioc_reader.collection.documents

# iterate over documents
for doc in docs:
    # show document ID (PubMed ID)
    print "PubMed ID:",doc.id
    # iterate over passages - PubMed titles and abstracts
    for passage in doc.passages:
        # show passage type
        print "Text type:", passage.infons['type']
        # iterate over annotations for each passage and show information
        for annotation in passage.annotations:
            print "Annotation ID:", annotation.id
            print "Annotation Type:", annotation.infons['type']
            print "Annotation Text:", annotation.text
            print "Offset and term length:", annotation.locations[0] 
    # line break
    print"\n"

"""
# output for the given file as an example:
PubMed ID: 1000475
Text type: title
Annotation ID: 0
Annotation Type: Disease
Annotation Text: pancreatic carcinoma
Offset and term length: 77:20
Annotation ID: 1
Annotation Type: Disease
Annotation Text: pancreatitis
Offset and term length: 102:12
Text type: abstract
Annotation ID: 2
Annotation Type: Disease
Annotation Text: carcinoma of the pancreas
Offset and term length: 232:25
Annotation ID: 3
Annotation Type: Disease
Annotation Text: pancreatitis
Offset and term length: 276:12
Annotation ID: 4
Annotation Type: Disease
Annotation Text: pancreatic disease
Offset and term length: 327:18
Annotation ID: 5
Annotation Type: Disease
Annotation Text: pancreatitis
Offset and term length: 492:12
Annotation ID: 6
Annotation Type: Disease
Annotation Text: pancreatic carcinoma
Offset and term length: 510:20
Annotation ID: 7
Annotation Type: Disease
Annotation Text: cancer
Offset and term length: 635:6
Annotation ID: 8
Annotation Type: Disease
Annotation Text: pancreatitis
Offset and term length: 700:12
Annotation ID: 9
Annotation Type: Disease
Annotation Text: pancreatic cancer
Offset and term length: 851:17
Annotation ID: 10
Annotation Type: Disease
Annotation Text: pancreatic disease
Offset and term length: 1096:18


PubMed ID: 1006519
Text type: title
Annotation ID: 0
Annotation Type: Disease
Annotation Text: ischemia
Offset and term length: 55:8
Text type: abstract
Annotation ID: 1
Annotation Type: Disease
Annotation Text: ischemia
Offset and term length: 866:8
Annotation ID: 2
Annotation Type: Disease
Annotation Text: claudication
Offset and term length: 906:12
Annotation ID: 3
Annotation Type: Disease
Annotation Text: pancreatic cancer
Offset and term length: 1628:17
Annotation ID: 4
Annotation Type: Disease
Annotation Text: myocardial infarct
Offset and term length: 1700:18


PubMed ID: 1010707
Text type: title
Annotation ID: 0
Annotation Type: Disease
Annotation Text: pancreatic cancer
Offset and term length: 13:17
Text type: abstract
Annotation ID: 1
Annotation Type: Disease
Annotation Text: pancreatic cancer
Offset and term length: 114:17
Annotation ID: 2
Annotation Type: Disease
Annotation Text: Pancreatic cancer
Offset and term length: 282:17
"""
