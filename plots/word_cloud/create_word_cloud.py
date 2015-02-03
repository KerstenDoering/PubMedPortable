#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script creates a word cloud based on a list of words and their frequencies.
"""

#Kersten Doering 29.11.2014, major change 03.02.2015
# inspired by https://github.com/atizo/PyTagCloud/blob/master/pytagcloud/test/tests.py

# PyTagCloud modules
from pytagcloud import create_tag_image, make_tags
# to use command-line parameters
from optparse import OptionParser

# main
if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="i", help='name of the input file that contains the logarithmic frequencies of each search term, e.g. "counts_surrounding_words_log.csv" or "counts_search_terms_log.csv"')
    parser.add_option("-o", "--output", dest="o", help='name of the output file which contains the word cloud, e.g. "cloud_surrounding_words.png" or "cloud_search_terms.png"')
    (options, args) = parser.parse_args()

    # no defaults set, show help message if no file names are given
    # use pairs "counts_surrounding_words_log.csv" and "cloud_surrounding_words.png" or "counts_search_terms_log.csv" and "cloud_search_terms.png"
    if not options.i or not options.o:
        parser.print_help()
    else:
        # save file names in an extra variable
        input_file = options.i
        output_file = options.o

        # save terms from CSV file in a list and convert their Floats to Integeters
        infile = open(input_file,"r")
        tag_list = []
        for line in infile:
            temp_line = line.strip().split("\t")
            tag_list.append((temp_line[0],(int(float(temp_line[1])))))

        # generate colour and size parameters for each term
        mtags = make_tags(tag_list)
        create_tag_image(mtags, output_file,size=(900, 600),background=(255, 255, 255, 255))
        infile.close()

