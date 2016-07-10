#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>
"""

# import modules
# to connect to Xapian
import xappy
# debug: sys.exit(0)
import sys
# path options
import os
# to connect to PostgreSQL
import psycopg2
from psycopg2 import extras
# runtime
import time

# get PMC ID from tbl_pmcid_name_pmid for the considered file name
def get_PMC(name):
    stmt = """
    SELECT 
        pmcid
    FROM 
        public.tbl_pmcid_name_pmid
    WHERE
        name = %s
    ;
    """ % name
    cursor.execute(stmt)
    output = cursor.fetchone()
    return output[0]

# set boolean flag to insert texts in PostgreSQL or in xapian data field
use_psql = True
# insert PMC ID and full text in PostgreSQL table
def insert_ID_and_text(pmcid, text):
    stmt = """
    INSERT INTO 
        tbl_pmcid_text 
    VALUES 
        (%s, %s)
    ;"""
    # use implicit escaping
    cursor.execute(stmt, (pmcid, text))

# build one index for each journal with this incrementing ID in a separate folder
counter = 0

# log starting time of the script
start = time.asctime()

# folder in which the indexes should be built
filePath = "files"

# settings for psql connection
postgres_user       = "parser"
postgres_password   = "parser"
postgres_host       = "localhost" 
postgres_port       = "5432"
postgres_db         = "pancreatic_cancer_db"
connection          = psycopg2.connect("dbname='"+postgres_db+"' user='"+postgres_user+"' host='"+postgres_host+"' password='"+postgres_password+"' port='"+postgres_port+"'")
cursor              = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

# get current directory
root = os.getcwd()
# mapping of journal names to indexing ID (counter)
f_ids = open(os.path.join(root,"ids.txt"),"w")
# some files do not contain a PMC ID (from file_list.txt)
f_log = open(os.path.join(root,"files_without_pmc.txt"),"w")
# directory xapian has to be created before
xapianPath = os.path.join( root, "xapian" )

# get all journal directories
directories = os.listdir(os.path.join(root,filePath))
# debug: use only one directory
#directories = ['Curr_HIV']
# there are nested directories that are not encoded as two directories in file_list.txt (only "Curr_HIV" is saved here in ids.txt, not 'AIDS_Rep':
# less file_list.txt | grep "Curr_HIV"
# 26/4b/Curr_HIV_AIDS_Rep_2010_Feb_27_7(1)_28-36.tar.gz   Curr HIV/AIDS Rep. 2010 Feb 27; 7(1):28-36      PMC2824118      PMID:20425055

# change into directory ("files") where the indexes will be built
os.chdir(os.path.join(root,filePath))
for directory in directories:
    os.chdir(directory)
    recent_filePath = os.getcwd()
    # get all subdirectories
    nested_directories = os.listdir(recent_filePath)
    # check whether there are subdirectories
    if os.path.isdir(nested_directories[0]):
        print directory,nested_directories
        # change into subdirectory
        recent_filePath = os.path.join(recent_filePath,nested_directories[0])
        os.chdir(recent_filePath)
    # get all documents in the currently selected journal directory
    files = os.listdir(recent_filePath)
    # store current indexing ID (used in ids.txt)
    recent_xapianPath = str(counter)
    # open a new file connection to create a Xapian index
    conn = xappy.IndexerConnection(os.path.join(xapianPath,recent_xapianPath))
    # create field to store the full texts
    conn.add_field_action('text', xappy.FieldActions.INDEX_FREETEXT, language='en')
    if not use_psql:
        # create a data field to store the full text in it, e.g. while iterating over search results
        conn.add_field_action('text', xappy.FieldActions.STORE_CONTENT)
    # iterate over all journal directories
    for file_name in files:
        doc = xappy.UnprocessedDocument() 
        f = open(os.path.join(recent_filePath,file_name),"r")
        text = f.read()
        f.close()
        doc.fields.append(xappy.Field("text", text))
        try:
            file_name = "'" + file_name + "'"
            pmcid = str(get_PMC(file_name))
            doc.id = pmcid
            if use_psql:
                insert_ID_and_text(pmcid, text)
        except:
            # possibly duplicates (from files_without_pmc.txt - less command shows the same content, although different formatting of line breaks, e.g.:
            # less Biosci_Rep_2012_Dec_1_32\(6\)_549-557.txt 
            # contains a PMC ID, but the following file not:
            # less Biosci_Rep_2012_Dec_1_32\(Pt_6\)_549-557.txt 
            # check the following PostgreSQL command and its result:
            # select * from tbl_pmcid_name_pmid where name like 'Biosci_Rep_2012_Dec_1_32%';
            # "PMC3497726";"Biosci_Rep_2012_Dec_1_32(6)_549-557.txt";22861139
            # store name in log file and continue with the next step
            f_log.write(file_name + "\n")
            continue
        # add this document to the currently selected index
        conn.add(doc)
    if use_psql:
        # one commit for each journal
        connection.commit()
    # change back into starting input directory ("files")
    os.chdir(os.path.join(root,filePath))

    # store documents and close connection
    conn.flush()
    conn.close()
    # iterate to next journal in the list of directories
    counter += 1

    # store mapping of ID (counter) to journal name
    f_ids.write(str(counter) + "\t" + directory + "\n")
# close files
f_ids.close()
f_log.close()

# close PostgreSQL connection
connection.close()

# show end of the calculation in command-line
end = time.asctime()
print "programme started - " + start
print "programme ended - " + end

