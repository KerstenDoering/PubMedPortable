#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2016, Kersten Doering <kersten.doering@gmail.com>
"""

# module to connect to PostgreSQL
import psycopg2

# insertion of PMC ID, file names from the gzip archives, and PubMed ID
def insert_IDs_and_Name(pmcid, name, pmid):
    stmt = """
    INSERT INTO 
        tbl_pmcid_name_pmid 
    VALUES 
        (%s, %s, %s)
    ;""" % (pmcid, name, pmid)
    cursor.execute(stmt)

# settings for PostgreSQL connection with user parser
postgres_user       = "parser"
postgres_password   = "parser"
postgres_host       = "localhost" 
postgres_port       = "5432"
postgres_db         = "pancreatic_cancer_db"
connection          = psycopg2.connect("dbname='"+postgres_db+"' user='"+postgres_user+"' host='"+postgres_host+"' password='"+postgres_password+"' port='"+postgres_port+"'")
cursor              = connection.cursor()

# open mapping file
infile = open("file_list.txt","r")
# the index is only used to show the number of uploaded lines on command-line
for index, line in enumerate(infile):
    temp = line.strip().split("\t")
    #example:
    #cc/25/BMC_Evol_Biol_2004_Oct_11_4_38.tar.gz	BMC Evol Biol. 2004 Oct 11; 4:38	PMC524511	PMID:15476555
    # first line contains the download time of file_list.txt
    if not "PMC" in line:
        continue
    # show progress
    if index % 1000000 == 0:
        print index, "PMC IDs inserted"
    pmcid = "'" + temp[2] + "'"
    name = "'" + temp[0].split("/")[-1].replace(".tar.gz",".txt")  + "'"
    try:
        # sometimes no PubMed ID is given
        pmid = temp[3].replace("PMID:","")
    except:
        pmid = "Null"
    insert_IDs_and_Name(pmcid, name, pmid)

# show final number of PMC IDs
print index, "PMC IDs inserted"
# commit
connection.commit()
# close connection
connection.close()
# close file
infile.close()
