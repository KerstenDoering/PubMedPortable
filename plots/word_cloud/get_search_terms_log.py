#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script transforms the frequencies of the search terms from the PubMedPortable documentation to logarithmic scale and writes the first 50 search terms to a CSV file.
"""

#Kersten Doering 29.11.2014, major change 03.02.2015

# to use command-line parameters
from optparse import OptionParser
# to join paths
import os
# to calculate logarithm
import math

# main
if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-x", "--xapian_path", dest="x", help='path to the directory containing the PubMedPortable scripts for generating the Xapian full text index',default="../../full_text_index_title_text")
    parser.add_option("-i", "--input", dest="i", help='name of the input file that contains the frequencies of each search term', default="results/counts_results.csv")
    parser.add_option("-o", "--output", dest="o", help='name of the output file with logarithmic frequencies', default="counts_search_terms_log.csv")
    parser.add_option("-n", "--number", dest="n", help='number of lines (default: 150)',default=150)
    (options, args) = parser.parse_args()

    # save file names in an extra variable
    input_file = options.i
    output_file = options.o
    xapian_path = options.x
    number = options.n 

    # save the first 150 (default number) terms in a CSV file
    infile = open(os.path.join(xapian_path,input_file),"r")
    outfile = open(output_file,"w")
    counter = 0
    for line in infile:
        if counter == number:
            break
        temp = line.strip().split("\t")
        #multiply the log value with 10 to receive a more precise scaling
        outfile.write(str(temp[0])+"\t"+str(int(math.log(float(temp[1]),10)*10))+"\n")
        counter += 1
    outfile.close()
    infile.close()
