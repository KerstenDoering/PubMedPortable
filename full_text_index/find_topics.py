#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Christian Senger <der.senger@googlemail.com>
"""

#Kersten Doering 09.07.2014

import psycopg2
from psycopg2 import extras
import sys
from optparse import OptionParser

#(dis)connection to psql database
def connect_postgresql():
    connection = psycopg2.connect("dbname='"+postgres_db+"' user='"+postgres_user+"' host='"+postgres_host+"' password='"+postgres_password+"'")
    #normal connection.cursor() gives back a list of tuples with fetchall(), DictCursor gives back a list of lists
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    return connection, cursor 

def disconnect_postgresql(connection, cursor):
    cursor.close()
#    connection.commit()
    connection.close()

#in this case, the special example of the author with most publications about "pancreatic cancer" is hard coded as a PostgreSQL query - just change parameters to do other queries
def get_pmids(cursor):
    #check this command in PGAdmin3
    #select distinct on(fk_pmid) * from pubmed.tbl_author where last_name = 'Friess' and (fore_name = 'H' or fore_name = 'Helmut') order by fk_pmid; \-- 370
    stmt = """
            SELECT 
                Distinct On(fk_pmid) fk_pmid
            FROM 
                pubmed.tbl_author
            WHERE
                last_name = 'Friess' 
            AND
                (fore_name = 'H' OR fore_name = 'Helmut') 
            ORDER BY
                fk_pmid;
        """
    cursor.execute(stmt)
    #if you want to give a parameter for a WHERE clause with %s in stmt, type in:
    #cursor.execute(stmt, (<parameter1>,<parameter2>,...))
    
    #return list of lists with fetchall() and DictCursor
    output = cursor.fetchall()
    return output

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-i", "--input_file", dest="i", help='name of the input file containing all PubMed-IDs and identified synonyms', default="results/pmids_results.csv")
    parser.add_option("-o", "--output_file", dest="o", help='name of the output file containing all PubMed-IDs belonging to a special author', default="results/pmids_results_from_author.csv")
    parser.add_option("-d", "--database", dest="d", help='name of the database to connect to', default="pancreatic_cancer_db")
    
    (options, args) = parser.parse_args()
    
    #save parameters in an extra variable
    input_file = options.i
    output_file = options.o
    
    #settings for psql connection
    postgres_user           = "parser"
    postgres_password       = "parser"
    postgres_host           = "localhost"
    postgres_port           = "5432"
    postgres_db = options.d


    #connect
    postgres_connection, postgres_cursor = connect_postgresql()

    #get_pmids returns a list of PubMed-IDs (with DictCursor) that only consists of [PubMed-ID]
    #use the zip function to return one large tuple with the first (and only) element of each list in the list and convert it to a list again
    pmid_list = get_pmids(postgres_cursor)
    pmid_list = list(zip(*pmid_list)[0])
    #debug:
    #print len(pmid_list)
    
    #open files
    infile = open(input_file,"r")
    outfile = open(output_file,"w")

    #if a pmid of the input file is in the author's publication list, write down this line in the output file
    for line in infile:
        pmid = line.strip().split("\t")[0]
        if int(pmid) in pmid_list:
            outfile.write(line)

    #close file pointers
    infile.close()
    outfile.close()

    #disconnect
    disconnect_postgresql(postgres_connection, postgres_cursor)
