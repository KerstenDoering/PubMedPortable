#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script downloads PubMed annotated abstracts in BioC XML format from PubTator. It wraps this command:
    curl -H "content-type:application/json" http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Disease/1000475,1006519,1010707/BioC/ > text_PubTator.xml
    The the type of annotation (here: Disease) can be easily exchanged for a given list of PubMed-IDs (as well as the BioC XML output format, but this is not intended here).
    Parameters: http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/tmTools/curl.html#
    The maximum number of PubMed-IDs to send to PubTator in this case is 21.
"""

# Kersten Doering 09.04.2015

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
    #return list of PubMed-IDs as a comma-separated string
    return ",".join(pmid_list)

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-i", "--infile", dest="i", help='name of the input file containing all PubMed-IDs, separated by line breaks (default: pmid_list.txt)', default="pmid_list.txt")
    parser.add_option("-o", "--outfile", dest="o", help='name of the output file containing all annotated abstracts in BioC format from PubTator (default: text_PubTator.xml)', default="text_PubTator.xml")
    parser.add_option("-l", "--logfile", dest="l", help='name of the logfile, e.g. text_PubTator.log (optional)')
    parser.add_option("-t", "--trigger", dest="t", help='name of the BioConcept, e.g.: Chemical, Disease, Gene, Mutation, or Species (default: Disease)', default="Disease")
    
    (options, args) = parser.parse_args()
    
    # save parameters in an extra variable
    log = options.l
    out = options.o
    infile = options.i
    trigger = options.t

    # get PubMed-IDs from file
    pmids = read_pmids(infile)
    # test case:
#    pmids = "1000475,1006519,1010707"
#    print "test case - processed PubMed-IDs:", pmids

    # BioC could be exchanged, e.g. with JSON
    p = subprocess.Popen(['curl','-H','"content-type:application/json"','http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/'+ trigger + '/'+pmids+'/BioC/'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # get annotated BioC XML file in variable stdout
    # stderr logs the command-line output
    stdout, stderr = p.communicate()
    outfile = open(out,"w")
    outfile.write(stdout)
    outfile.close()

    if log:
        logfile = open(log,"w")
        logfile.write(stderr)
        logfile.close()

