#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Christian Senger <der.senger@googlemail.com>
"""
#Kersten Doering 16.06.2014

if __name__=="__main__":

    from operator import itemgetter
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="f", help='name of the input file containing all identified synonyms', default="results.csv")
    
    (options, args) = parser.parse_args()
    
    #save parameters in an extra variable
    file_name = options.f


    #read results from Xapian synonym search
    infile = open("results/"+file_name,"r")
    pmid_synonym = {}
    synonym_count = {}
    for line in infile:
        temp = line.strip().split("\t")
        #temp[0] is pmid, temp[1] is synonym
        #create new key-value pair with pmid and list of synonyms found or append new synonym
        if not temp[0] in pmid_synonym:
            pmid_synonym[temp[0]] = [temp[1]]
        elif not temp[1] in pmid_synonym[temp[0]]:
            pmid_synonym[temp[0]].append(temp[1])
        #count pmids for synonyms
        if not temp[1] in synonym_count:
            synonym_count[temp[1]] = 1
        else:
            synonym_count[temp[1]] +=1
    infile.close()

    #sort dictionary of synonym-count tuples and save it with file name "counts_<input_file_name>.csv"
    sorted_counts = sorted(synonym_count.items(), key=itemgetter(1), reverse = True)
    outfile = open("results/counts_"+file_name,"w")
    for count in sorted_counts:
            outfile.write(str(count[0])+"\t"+str(count[1])+"\n")
    outfile.close()

    #sort dictionary pmids and add all synonyms tab-separated in a line
    sorted_pmids = sorted(pmid_synonym.items(), key=itemgetter(0), reverse = False)
    outfile = open("results/pmids_"+file_name,"w")
    for synonyms in sorted_pmids:
            outfile.write(str(synonyms[0])+"\t"+str("\t".join(synonyms[1]))+"\n")
    outfile.close()

