#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Christian Senger <der.senger@googlemail.com>
"""

#Kersten Doering 09.07.2014

import psycopg2
from psycopg2 import extras

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

def get_authors(cursor):
    #check this command in PGAdmin3
    #select fk_pmid, last_name, fore_name from pubmed.tbl_author order by fk_pmid;
    stmt = """
            SELECT 
                fk_pmid, last_name, fore_name
            FROM 
                pubmed.tbl_author
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
    parser.add_option("-f", "--file", dest="f", help='name of the output file containing all identified synonyms', default="authors.csv")
    parser.add_option("-d", "--database", dest="d", help='name of the database to connect to', default="pancreatic_cancer_db")
    
    (options, args) = parser.parse_args()
    
    #save parameters in an extra variable
    file_name = options.f
    
    #settings for psql connection
    postgres_user           = "parser"
    postgres_password       = "parser"
    postgres_host           = "localhost"
    postgres_port           = "5432"
    postgres_db = options.d


    #connect
    postgres_connection, postgres_cursor = connect_postgresql()

    #get_authors returns a list of lists (with DictCursor) that consists of [PubMed-ID, last name, fore name]
    publication_list = get_authors(postgres_cursor)

    #save "last_name, fore_name" as key and list of PubMed-IDs as value
    publication_dict = {}
    
    #iterate over complete list
    for triple in publication_list:
        #concatenate strings of last name (triple[1]) and fore name (triple[2]) - end of list
        #if there is no last or fore name, add a special string to recognise them afterwords
        #in these cases there is only a collective name - try this command in PGAdmin3:
        #--select * from pubmed.tbl_author where last_name is NULL and fore_name is NULL;
        try:
            name = ", ".join(triple[1:])
#            print "name:" + name
        except:
            if triple[1] == None and triple[2] == None:
                name = "not_selected_collection_name"
            elif triple[1] == None:
                name = "no_last_name, "+triple[2]
            elif triple[2] == None:
                name = triple[1]+", no_fore_name"

        #if name is not yet a key, initialise it with a one-element-list of the first PubMed-ID that can be extended
        if not name in publication_dict:
            publication_dict[name] = [triple[0]]
        #else append PubMed-ID
        elif name in publication_dict and not triple[0] in publication_dict[name]:
            publication_dict[name].append(triple[0])

        #there should be no double PubMed-ID entries, but there are some - maybe author names that sound exactly the same?:
        """
        else:
            print triple[0] 
        """

    #save number of publications as tuples with (number, author)
    pubs_number = []
    #iterate over all authors and pmids and count number of publications
    for author, pmids in publication_dict.items():
        #debug:
        #print author, pmids
        pubs_number.append((len(pmids),author))

    #sort number of publications in descending order
    pubs_number.sort(reverse= True)
    
    #save list of publictions in file "results/authors.csv", first column author, second column number of publications
    outfile = open("results/" + file_name,"w")
    #debug:
    #for tuples in pubs_number[0:10]:
    for tuples in pubs_number:
        #debug:
        #print tuples[1], ": ", tuples[0]
        outfile.write(tuples[1]+"\t"+str(tuples[0])+"\n")
    outfile.close()

    #debug:
    #print len(publication_dict)

    #disconnect
    disconnect_postgresql(postgres_connection, postgres_cursor)
