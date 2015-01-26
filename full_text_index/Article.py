#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Christian Senger <der.senger@googlemail.com>
"""

import xappy
import sys

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from SynonymParser import SynonymParser

class Article():
    
    user          = "parser"
    password      = "parser"
    host          = "localhost"
    port          = "5432"
    db            = ""
    con           = "postgresql://"+user+":"+password+"@"+host+":"+port+"/"

    #Kersten: set these attributes when calling static function getConnection(database)
    base          = None#declarative_base()
    engine        = None#create_engine(__con, pool_recycle = 900, echo=False)
    base          = None#__base.metadata.create_all(__engine)
    session       = None#sessionmaker(bind=__engine)()    

    __count         = 0
    __countMsg      = ""

    def __init__(
                 self,
                 pmid
                 ):

        self.__pmid     = int(pmid)
        self.__title    = None
        self.__abstract = None
        self.__chemicals= []
        self.__keywords = []
        self.__mesh     = []
        
        self.__loadStub()
        self.__loadChemicals()
        self.__loadKeywords()
        self.__loadMeSH()
    
        Article.__count     += 1
        nbs                 = len(Article.__countMsg)        
        Article.__countMsg  = "article %s created" % (str(Article.__count))
        sys.stdout.write('\b' * nbs + Article.__countMsg)
        
    @staticmethod
    def getConnection(database):
        
        Article.con           = "postgresql://"+Article.user+":"+Article.password+"@"+Article.host+":"+Article.port+"/"+database
        Article.base          = declarative_base()
        Article.engine        = create_engine(Article.con, pool_recycle = 900, echo=False)
        Article.base          = Article.base.metadata.create_all(Article.engine)
        Article.session       = sessionmaker(bind=Article.engine)()
        

    def getPMID(self):
        return self.__pmid
    
    def getTitle(self):
        return self.__title
    
    def getAbstract(self):
        return self.__abstract
    
    def getChemicals(self):
        return self.__chemicals
    
    def getKeywords(self):
        return self.__keywords

    def getMeSH(self):
        return self.__mesh

    def __loadStub(self):
            pmid = str(self.__pmid)
            #print "####",pmid,"####"#in this case it is always one pmid - it is not a "complete" join
            stmt = """
            SELECT 
                pmid,
                article_title as title,
                abstract_text as abstract
            FROM 
                pubmed.tbl_medline_citation
                    LEFT OUTER JOIN
                pubmed.tbl_abstract
                        ON pmid = fk_pmid
            WHERE
                pmid = '"""+pmid+"""'
            ;
            """
        
            articles = Article.session.query(
                    "pmid",
                    "title",
                    "abstract"
            ).from_statement(stmt)
            
            for article in articles:
                self.__title    = article.title
                self.__abstract = article.abstract
                break;

    def __loadChemicals(self):
        pmid = str(self.__pmid)
        
        stmt = """
            SELECT 
                name_of_substance AS substance
            FROM 
                pubmed.tbl_chemical
            WHERE
                fk_pmid = '"""+pmid+"""'
            ORDER BY 
                name_of_substance;
        """    

        
        substances = Article.session.query(
                    "substance"
        ).from_statement(stmt)
        
        for substance in substances:
            self.__chemicals.append(substance.substance)

    def __loadKeywords(self):
        pmid = str(self.__pmid)
        
        stmt = """
            SELECT 
                keyword
            FROM 
                pubmed.tbl_keyword
            WHERE
                fk_pmid = '"""+pmid+"""'
            ORDER BY 
                keyword;
        """    

        
        keywords = Article.session.query(
                    "keyword"
        ).from_statement(stmt)
        
        for keyword in keywords:
            self.__keywords.append(keyword.keyword)

    def __loadMeSH(self):
        pmid = str(self.__pmid)
        
        stmt = """
            SELECT 
                descriptor_name
            FROM 
                pubmed.tbl_mesh_heading
            WHERE
                fk_pmid = '"""+pmid+"""'
            ORDER BY 
                descriptor_name;
        """    

        
        mesh_terms = Article.session.query(
                    "descriptor_name"
        ).from_statement(stmt)
        
        for descriptor_name in mesh_terms:
            self.__mesh.append(descriptor_name.descriptor_name)

    @staticmethod
    def getArticlesByYear(b_year, e_year):
        b_year            = int(b_year)
        e_year            = int(e_year)
        
        
        stmt = """
            SELECT 
                pmc.fk_pmid
            FROM 
                pubmed.tbl_journal pmc
            WHERE
                pub_date_year >= """+str(b_year)+"""
                    AND
                pub_date_year <= """+str(e_year)+"""
           
        ;
        """ 

        pmids = Article.session.query(
                    "fk_pmid"
        ).from_statement(stmt)
        return [Article(pmid.fk_pmid) for pmid in pmids]

    
    @staticmethod
    def closeConnection():
        Article.session.close()

