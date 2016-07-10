#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2016, Kersten Doering <kersten.doering@gmail.com>
"""

# import modules
# to connect to Xapian
import xappy
# debug: sys.exit(0)
import sys
# path options
import os
# runtime
import time
# to connect to PostgreSQL
import psycopg2
from psycopg2 import extras

# log start time
start = time.asctime()

# set options verbose, output and whether PostgreSQL should be used to display results
output = True
verbose = True
debug = False
use_psql = True

# get path to this script
root = os.getcwd()

# search connection to Xapian full text index
xapianPath   =  os.path.join( root, "xapian_PMC_complete" )
searchConn = xappy.SearchConnection(xapianPath)
searchConn.reopen()

# get PMC texts from PostgreSQL
def get_text(pmcid):
    stmt = """
    SELECT 
        text
    FROM 
        public.tbl_pmcid_text
    WHERE
        pmcid = %s
    ;
    """ 
    cursor.execute(stmt, (pmcid,))
    output = cursor.fetchone()
    return output[0]

# settings PostgreSQL connection with user parser
postgres_user       = "parser"
postgres_password   = "parser"
postgres_host       = "localhost" 
postgres_port       = "5432"
postgres_db         = "pancreatic_cancer_db"
connection          = psycopg2.connect("dbname='"+postgres_db+"' user='"+postgres_user+"' host='"+postgres_host+"' password='"+postgres_password+"' port='"+postgres_port+"'")
cursor              = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

# get search terms (synonyms)
synonyms = []
infile = open("synonyms/synonyms.txt","r")
for line in infile:
    synonyms.append(line.strip())
infile.close()

# write results to file with PMC ID and identified synonym if option output
if output:
    outfile = open("results/results.csv","w")
# search synonyms
for term in synonyms:
    # use exact search with quotations
    text = '"'+term + '"'
    # build query
    query = searchConn.query_field('text', text )
    # show query syntax if option verbose:
    if verbose:
        print query
    # search and get results
    results=searchConn.search(query, 0, searchConn.get_doccount())
    # iterate over results
    for r in results:
        # write to file if option output:
        if output:
            outfile.write(r.id + "\t" + term + "\n")
        # option verbose:
        if verbose and not use_psql:
            print "################"
            print r.id
            print r.data['text'][0][0:90] + "..."
            print "################"
        if verbose and use_psql:
            print "################"
            print r.id
            print get_text(r.id)[0:90] + "..."
            print "################"
        # terminate here to have a look at the first result if option debug:
        if debug:
            sys.exit(0)
    # show number of results if option verbose
    if verbose:
        print "#results: ", len(results)
# close file if option output
if output:
    outfile.close()

# log end time
end = time.asctime()

# show runtime
print "programme started - " + start
print "programme ended - " + end

