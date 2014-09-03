#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Christian Senger <der.senger@googlemail.com>
"""

#Kersten 13.06.2014:
#"python RunXapian.py -x" for indexing and searching
#"python RunXapian.py -f" for indexing
#"python RunXapian.py" for searching
#"python -h" for help

import xappy
import os.path

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from SynonymParser import SynonymParser
from PubMedXapian import PubMedXapian

if __name__=="__main__":
    #new Code Kersten 08.07.2014
    from optparse import OptionParser


    parser = OptionParser()
    parser.add_option("-b", "--b_year", dest="b", help="year of the index to begin parsing (default: 1809)", default=1809)
    parser.add_option("-p", "--xapian_database_path", dest="xapian_database_path", help="Specify the path to the Xapian full text index.", default="xapian")
    parser.add_option("-e", "--e_year", dest="e", help="year of the index to end parsing (default: 2014)", default=2014)
    parser.add_option("-x", "--index", dest="x", action="store_true", default=False, help="Create Xapian index first (default: False)")
    parser.add_option("-s", "--synoynm_path", dest="s", help="relative path to synonym list (default: synonyms/pancreatic_cancer.txt)", default = "synonyms/pancreatic_cancer.txt")
    parser.add_option("-d", "--db_psql", dest="d", help="database in PostgreSQL to connect to (default: pancreatic_cancer_db)", default = "pancreatic_cancer_db")
    parser.add_option("-f", "--no_search", dest="f", action="store_false", help="find synonyms in Xapian database (default: True)", default=True)
    parser.add_option("-r", "--results_name", dest="r", help="name of the results file (default: results.csv)", default = "results")
    parser.add_option("-n", "--name_xapian_db", dest="n", help="name of the xapian database folder (default: xapian<e_year>)", default = "xapian")
    
    (options, args) = parser.parse_args()
    
    #in PubMed, first articles published are from 1809:
    #http://www.nlm.nih.gov/bsd/licensee/2013_stats/baseline_med_filecount.html
    #set range of years
    b_year = options.b
    e_year = options.e

    #set results filename
    filename = options.r

    #set Xapian database name (default: "xapian<e_year>")
    if options.n == "xapian":
        xapian_name = options.n + str(options.e)
    else:
        xapian_name = options.n
        print xapian_name

    #set PSQL database name
    database = options.d
    #set synonym path
    synonymPath = options.s

    ##debug:
#    print "beginning with year:"
#    print b_year
#    print "ending with year:"
#    print e_year

    #Synonym file to use
    if not (os.path.isfile(synonymPath)):
        print "synonym file not existing - programme terminates"
        exit(0)

    if options.x:
        #import class Article from Article.py and connect to PostgreSQL database
        from Article import Article
        Article.getConnection(database)
        #select all articles in a range of years x >= b_year and x <= e_year
        articles = Article.getArticlesByYear(b_year,e_year)
        ### debug:
#        print "###",len(articles),"###"
        Article.closeConnection()
        print "\n-------------"
        print "processing files from year " + str(b_year) + " to " + str(e_year)
        print "-------------"
        print "got articles from PostgreSQL database"
        print "-------------"
    #take the last year to create directory
    indexer  = PubMedXapian(xapian_name, xapianPath = options.xapian_database_path)
    #build full text index with Xapian for all articles selected before
    if options.x:
       print "now indexing articles in Xapian"
       indexer.buildIndexWithArticles(articles)
       print "\n-------------"
    if not (os.path.isdir("xapian/"+xapian_name)):
        print "xapian files are not existing"
        parser.print_help()
        exit(0)
    if options.f:
        synonymParser = SynonymParser(synonymPath, indexer, filename)
        synonymParser.parseAndFind()
        if filename == "results":
            print "\nquery results written to " + filename + ".csv"
        else:
            print "\nquery results written to " + filename
    else:
        print "no search of synonyms performed, use \"python RunXapian.py -h\" for parameter view"

