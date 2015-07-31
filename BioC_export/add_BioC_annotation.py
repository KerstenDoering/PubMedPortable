#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script adds MeSH term annotations to a given XML document in BioC format consisting of PubMed abstracts.
"""

# Kersten Doering 29.01.2015
# inspired by https://github.com/2mh/PyBioC/tree/master/src/stemmer.py

# to connect to PostgreSQL database with psycopg2
import psycopg2
# to use dictionary cursor
from psycopg2 import extras
# to parse command-line parameters
from optparse import OptionParser
# to get MeSH term positions from a given abstract
import re
# import PyBioC modules (use given github project here as stemmer.py is used)
from bioc import BioCReader
from bioc import BioCWriter
from bioc import BioCAnnotation
from bioc import BioCLocation
# only PubMed-IDs without an abstract text will generate an error in case of merging annotated BioC XML files from PubTator
import sys

# get MeSH terms from PostgreSQL database
def get_MeSH_terms(pmid):
    # SQL command for a given PubMed-ID
    stmt = """
    SELECT 
        descriptor_name
    FROM 
        pubmed.tbl_mesh_heading
    WHERE
        fk_pmid = '"""+pmid+"""'
    ;
    """
    #get MeSH terms
    cursor.execute(stmt)
    output = cursor.fetchall()
    #this cursor returns a list of lists - reduce output by 1 dimension to return a single list (works for several elements or one element)
    #if the PubMed-ID does not exist in this database or simply no MeSH term is given, return None
    if output:
        return list(zip(*output)[0])
    else:
        return None

# add annotation with infon, location, and text for a given triple with start position, term length, and MeSH term
def add_annotation(triple, annotation_id):
    # initialize annotation element
    bioc_annotation = BioCAnnotation()
    # MeSH term in a tag <text> ... </text> (origininal term, searched case insensitive)
    bioc_annotation.text = triple[2]
    # generate XML structure for the annotation and add infon
    bioc_annotation.id = str(annotation_id)
    bioc_annotation.put_infon('type', 'MeSH term')
    # add location element
    bioc_location = BioCLocation()
    # add length of MeSH term
    bioc_location.length = str(triple[1])
    # add start position (offset) 
    bioc_location.offset = str(triple[0])
    bioc_annotation.add_location(bioc_location)
    return bioc_annotation

# main
if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-i", "--infile", dest="i", help='name of the BioC XML input file containing PubMed abstracts', default="text_BioC.xml")#text_PubTator.xml
    parser.add_option("-b", "--bioc", dest="b", help='name of the XML Document Type Definition file (DTD file) presenting BioC semantics', default="BioC.dtd")
    parser.add_option("-o", "--outfile", dest="o", help='name of the output file with annotated MeSH terms in BioC XML format', default="annotated_text_BioC.xml")#annotated_text_PubTator.xml
    parser.add_option("-d", "--database", dest="d", help='name of the database to connect to', default="pancreatic_cancer_db")
    
    (options, args) = parser.parse_args()

    # settings for psql connection
    postgres_user       = "parser"
    postgres_password   = "parser"
    postgres_host       = "localhost" 
    postgres_port       = "5432"
    postgres_db         = options.d
    connection = psycopg2.connect("dbname='"+postgres_db+"' user='"+postgres_user+"' host='"+postgres_host+"' password='"+postgres_password+"' port='"+postgres_port+"'")
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # save file names in an extra variable
    input_file  = options.i
    dtd_file    = options.b
    output_file = options.o

    # open input files
    try:
        bioc_reader = BioCReader(input_file, dtd_valid_file=dtd_file)
        bioc_reader.read()
    except:
        ## debug:
        #raise
        sys.exit("Probably, your input file contains an empty passage. Maybe one of the PubMed-IDs does not have an abstract. Please, remove empty passage and document tags. No output file was written.")

    # the elements <date> and <key> will not be changed or updated by this script (it only adds (MeSH) annotations)
    # define output file
    bioc_writer = BioCWriter(output_file)
    # initialization for reading input file
    bioc_writer.collection = bioc_reader.collection
    # get documents (one PubMed-ID with title and text equals one document)
    docs = bioc_writer.collection.documents
    # different annotation IDs can be confusing - add a type to the iterating number
    annotation_type = "_MeSH"
    # iteration over PubMed abstracts with ID, title, and text
    for doc in docs:
        # get MeSH terms from PostgreSQL database
        mesh_terms = get_MeSH_terms(doc.id)
        # use annotation IDs starting at 0 for each document
        annotation_id = 0
        # if at least one MeSH term was found for this PubMed-ID (doc.id)
        if mesh_terms:
            # abstract title is one passage and abstract text is one passage
            for passage in doc:
                # first save all occurrences of terms for a document passage with position and length, sort them afterwards, and then create infons with incremental annotation ID
                occurrences = []
                for mesh in mesh_terms:
                    #search for start and end positions with case insensitivity
                    #if there is no abstract (no passage.text) in the document, the regex search will result in an error - use try-except block
                    try: 
                        positions = [(a.start(), a.end()) for a in list(re.finditer(mesh.lower(), passage.text.lower()))]
                        if positions:
                            for tuples in positions:
                                #passage.text[tuples[0]:tuples[0]+len(mesh)] would return the identified term
                                 # the triple is (start position, term length, MeSH term)
                                occurrences.append((tuples[0], len(mesh), mesh))
                    except:
                            print doc.id, mesh, "Mesh term not found."
                # sorted by start positions
                occurrences.sort()
                for triple in occurrences:
                    # ToDo: add a condition for nested tags?
                    # add annotation with infon, location, and text
                    bioc_annotation = add_annotation(triple,str(annotation_id)+annotation_type)
                    passage.add_annotation(bioc_annotation)
                    # increment annotation_id
                    annotation_id += 1
    # write XML format to output file
    bioc_writer.write()
    # debug:
    #print(bioc_writer)

    # disconnect from database
    cursor.close()
    connection.close()
