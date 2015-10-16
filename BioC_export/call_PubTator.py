#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script downloads PubMed annotated abstracts in BioC XML format from PubTator. It wraps this command:
    curl -H "content-type:application/json" http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Disease/1000475,1006519,1010707/BioC/ > text_PubTator.xml
    The the type of annotation (here: Disease) can be easily exchanged for a given list of PubMed-IDs (as well as the BioC XML output format). The maximum number of PubMed-IDs to send to PubTator (tested) is 21. Unfortunately, articles without abstract are not processed, but there is the possibility to submit raw text.
    Parameters: http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/tmTools/#curl
"""

# module that wraps command-line parameters and is able to pipe the output
import subprocess
# parse parameters given for this script
from optparse import OptionParser

# read PubMed-IDs from file and return them as a comma-separated string
def read_pmids(infile):
    #open file with PubMed-IDs
    f = open(infile,"r")
    #save all IDs in a list
    pmid_list = []
    for line in f:
        pmid_list.append(line.strip())
    #close file
    f.close()
    #return list of PubMed-IDs
    return pmid_list

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-i", "--infile", dest="i", help='name of the input file containing all PubMed-IDs, separated by line breaks (default: pmid_list.txt)', default="pmid_list.txt")
    parser.add_option("-o", "--outfile", dest="o", help='name of the output file containing all annotated abstracts in BioC format from PubTator (default: text_PubTator.xml)', default="text_PubTator.xml")
    parser.add_option("-l", "--logfile", dest="l", help='name of the logfile, e.g. text_PubTator.log (optional)')
    parser.add_option("-t", "--trigger", dest="t", help='name of the BioConcept, e.g.: Chemical, Disease, Gene, Mutation, or Species (default: Disease)', default="Disease")
    parser.add_option("-f", "--format", dest="f", help='name of the output format, e.g.: BioC, JSON, or PubTator (default: BioC)', default="BioC")
    (options, args) = parser.parse_args()
    
    # save parameters in an extra variable
    log = options.l
    out = options.o
    infile = options.i
    trigger = options.t
    output_format = options.f

    # get PubMed-IDs from file
    pmids = read_pmids(infile)
    # test case:
#    pmids = [1000475,1006519,1010707]
#    print "test case - processed PubMed-IDs:", pmids

    # if a file consists of more than 20 PubMed-IDs, split the list to blocks of 20 and add the results to the main output file (out)
    if len(pmids) > 20:
        # if log parameter is true, open file for writing
        if log:
            logfile = open(log,"w")
        # open output file
        outfile = open(out,"w")
        # check how many times the PubTator command has to be executed
        limit = len(pmids) / 20
        # if the number is not equal to a multiple of 20, add +1 one to the number of PubTator calls (the last one will be a block with less than 20 PubMed-IDs)
        if not len(pmids) % 20 == 0:
            limit += 1
        # iterate over the number of times, PubTator has to be called
        for i in range(limit):
            # debug - one block contains 20 PubMed-IDs, i = 100 equals 2,000 PubMed-IDs:
#            if i % 100 == 0:
#                print i
            # block of 20 pmids
            pmids_set = pmids[i*20:(i+1)*20]
            # generate a string of comma-separated PubMed-IDs
            pmids_set = ",".join(pmids_set)
            # call PubTator with subprocess and curl
            # man curl: (HTTP) Extra header to use when getting a web page. [...]
            p = subprocess.Popen(['curl','-H','"content-type:application/json"','http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/'+ trigger + '/'+pmids_set+'/' + output_format + '/'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # get annotated BioC XML, JSON, or PubTator file in variable stdout
            # stderr logs the command-line output
            stdout, stderr = p.communicate()
            # store PubTator output in outfile
            outfile.write(stdout)
            # if log parameter is true, store log information
            if log:
                logfile.write(stderr)
        # if log parameter is true, close file
        if log:
            logfile.close()
        # close output file
        outfile.close()
    # if the number of PubMed-IDs is less equal to 20, the command to call PubTator will be executed only ones
    else:
        # generate a string of comma-separated PubMed-IDs
        pmids = ",".join(pmids)
        # call PubTator with subprocess and curl
        p = subprocess.Popen(['curl','-H','"content-type:application/json"','http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/'+ trigger + '/'+pmids+'/' + output_format + '/'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # get annotated file in variable stdout
        # stderr logs the command-line output
        stdout, stderr = p.communicate()
        # store PubTator output in outfile
        outfile = open(out,"w")
        outfile.write(stdout)
        outfile.close()
        # if log parameter is true, store log information
        if log:
            logfile = open(log,"w")
            logfile.write(stderr)
            logfile.close()

