#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script reads annotations from a given XML document in BioC format and writes the annotations tab-separated to a CSV file.
"""

# PyBioC API
from bioc import BioCReader

# open BioC XML file and DTD file with XML structure definitions
bioc_reader = BioCReader("pancreatic_cancer_BioC_DNorm.xml", dtd_valid_file="BioC_DNorm.dtd")
# read files
bioc_reader.read()
# get documents from BioC XML file (PubMed abstracts)
docs = bioc_reader.collection.documents

# output file
out = open("DNorm_formatted.csv","w")

# iterate over documents (each document ID is a PubMed ID)
for index,doc in enumerate(docs):
    # debug: show status - every 1,000 PubMed IDs
    if index % 1000 == 0:
        print index
    # iterate over passages (titles and texts)
    for passage in doc.passages:
        # iterate over annotations for each passage and write them to file
        for annotation in passage.annotations:
            # write <PubMed ID>\t<disease synonym>\t<MeSH identifier>
            # there are annotations without MeSH identifier
            try:
                out.write(str(doc.id) + "\t" + annotation.text + "\t" + annotation.infons['MESH'] + "\n")
            except:
                print doc.id, annotation.text, annotation.infons['type']

# close file
out.close()
