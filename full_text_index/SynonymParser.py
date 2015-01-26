#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Christian Senger <der.senger@googlemail.com>
"""

import xappy
import sys

class SynonymParser():

    __msg       = ""
    __cidCount  = 0

    def __init__(self, path, pubMedXapian, filename):
        self.__path         = path
        self.__pubMedXapian = pubMedXapian
        if ".csv" in filename or ".txt" in filename:
            self.__outfile      = open("results/"+filename,'w')
        else:
            self.__outfile      = open("results/"+filename+".csv",'w')
        
    def parseAndFind(self):

        for row in open(self.__path):
            synonym = row.strip()
            pmids = self.__pubMedXapian.findPMIDsWithSynonyms([synonym])
            for pmid in pmids: 
                self.__outfile.write(str(pmid)+"\t"+str(synonym)+"\n")
            SynonymParser.__cidCount += 1                    
            nbs                 = len(SynonymParser.__msg)        
            SynonymParser.__msg  = "number of synonyms searched: %s " % (str(SynonymParser.__cidCount))
            sys.stdout.write('\b' * nbs + SynonymParser.__msg)

