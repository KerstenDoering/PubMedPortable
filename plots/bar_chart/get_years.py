#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script connects to a PostgreSQL database and selects all publication years given for a list of PubMed-IDs. The PubMed-IDs are provided by the search on the Xapian full text index for the pancreatic cancer data set. The output contains three CSV files that can be used to create a timeline for the search terms by using the script create_bar_chart.py.
"""

#Kersten Doering 11.06.2014

# to connect to a PostgreSQL relational database
import psycopg2
# to use DictCursor
from psycopg2 import extras
# to join paths
import os
# to use command-line parameters
from optparse import OptionParser
# to count occurrences of an Integer in a list: http://stackoverflow.com/questions/2600191/how-can-i-count-the-occurrences-of-a-list-item-in-python
from collections import Counter

# join abstract title and text for a given PubMed-ID "pmid" and return the triple as a list [PubMed-ID, title, text]
def get_year(pmid):
    stmt = """
            SELECT 
                pub_date_year
            FROM 
                pubmed.tbl_journal
            WHERE
                fk_pmid = %s
        """
        
    cursor.execute(stmt, (pmid,))
    
    year = cursor.fetchone()
    return year

# main
if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-d", "--database", dest="d", help='name of the database to connect to', default="pancreatic_cancer_db")
    parser.add_option("-x", "--xapian_path", dest="x", help='path to the directory containing the PubMedPortable scripts for generating the Xapian full text index',default="../../full_text_index_title_text")
    parser.add_option("-p", "--pmids_input", dest="p", help='name of the input file that contains all PubMed-IDs for the search term', default="results/results.csv")
    parser.add_option("-t", "--terms_input", dest="t", help='name of the input file that contains all search terms that should be shown in the bar chart', default="search_terms.txt")
    parser.add_option("-o", "--output_folder",dest="o",help='name of the output directory (optional, default: ""', default="")
    (options, args) = parser.parse_args()

    # settings for psql connection
    postgres_user       = "parser"
    postgres_password   = "parser"
    postgres_host       = "localhost" 
    postgres_port       = "5432"
    postgres_db         = options.d
    connection          = psycopg2.connect("dbname='"+postgres_db+"' user='"+postgres_user+"' host='"+postgres_host+"' password='"+postgres_password+"' port='"+postgres_port+"'")
    cursor              = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # save file paths in an extra variable
    pmids_input         = options.p
    terms_input         = options.t
    xapian_path         = options.x
    output_path         = options.o

    # search terms for RunXapian.py - save in dictionary search_terms, prepare the dictionary for the publication years:
    search_terms = {}
    years = {}
    infile = open(terms_input,"r")
    for line in infile:
        search_terms[line.strip()] = []
        years[line.strip()] = []
    infile.close()

    # results from RunXapian.py - save PubMed-IDs for each search term in a list of pmids:
    infile = open(os.path.join(xapian_path, pmids_input),"r")
    for line in infile:
        temp_line = line.strip().split("\t")
        if temp_line[-1] in search_terms:
            search_terms[temp_line[-1]].append(temp_line[0])
    infile.close()

    # get all years for each search term
    for search_term, pmids in search_terms.items():
        for pmid in pmids:
            year = get_year(pmid)
            if year:
                years[search_term].append(int(year[0]))

    # count years and save the numbers in a CSV file named with the gene name
    for search_term, year_list in years.items():
        # use module collections with Counter() to generate a dictionary with the key year and the amount of years as value
        counts = Counter(year_list)
        # sort list of appearing years
        temp_years = counts.keys()
        temp_years.sort(reverse=True)
        # save lists of years in a CSV file with search_term as name
        outfile = open(os.path.join(output_path,search_term) + ".csv","w")
        for year in temp_years:
            outfile.write(str(year) + "," + str(counts[year]) + "\n")
        outfile.close()
