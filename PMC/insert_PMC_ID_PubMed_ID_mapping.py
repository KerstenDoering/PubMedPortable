#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2016, Kersten Doering <kersten.doering@gmail.com>
"""

# module to connect to PostgreSQL
import psycopg2

# insertion of PMC ID and PubMed ID from PMC-ids.csv
def insert_IDs_and_Name(pmcid, pmid):
    stmt = """
    INSERT INTO 
        tbl_pmcid_pmid 
    VALUES 
        (%s, %s)
    ;""" % (pmcid, pmid)
    cursor.execute(stmt)

# settings PostgreSQL connection with user parser
postgres_user       = "parser"
postgres_password   = "parser"
postgres_host       = "localhost" 
postgres_port       = "5432"
postgres_db         = "pancreatic_cancer_db"
connection          = psycopg2.connect("dbname='"+postgres_db+"' user='"+postgres_user+"' host='"+postgres_host+"' password='"+postgres_password+"' port='"+postgres_port+"'")
cursor              = connection.cursor()

# open mapping file
infile = open("PMC-ids.csv","r")
# the index is only used to show the number of uploaded lines on command-line
for index, line in enumerate(infile):
    if line.startswith("Journal Title,"):
        continue
    # show progress
    if index % 1000000 == 0:
        print index, "PMC IDs inserted"
        connection.commit()
    temp = line.split(",PMC")[1].split(",")
    pmcid = "'PMC" + temp[0] + "'"
    # sometimes no PubMed ID is given
    if not temp[1] == "":
        pmid = temp[1]
    else:
        pmid = "Null"
    insert_IDs(pmcid, pmid)

# show final number of PMC IDs
print index, "PMC IDs inserted"
# commit
connection.commit()
# close connection
connection.close()
# close file
infile.close()
