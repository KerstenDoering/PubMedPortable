#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script extracts Entrez GeneID numbers for a specific gene name (hard-coded gene name KRAS and protein name K-ras) from the GeneTUKit output file.
"""

# open file
infile = open("GeneTUKit_formatted.csv","r")
# use a dictionary to store identifier and synonym
dictionary = {}
# iterate over lines in file
for line in infile:
    # split tab-separated line
    temp = line.split("\t")
    # check whether the gene or protein name is contained in this line (lowercase)
    if "kras" in temp[1].lower() or "k-ras" in temp[1].lower():
        # check whether identifier is already contained in dictionary (no else case)
        # the synonyms are just stored to visually inspect the identifier
        if not temp[2] in dictionary:
            dictionary[temp[2]] = temp[1]
# write to this file
outfile = open("search_terms_KRAS.txt","w")
# iterate over all entries in the dictionary and store them in the output file
for identifier,synonym in dictionary.items():
    outfile.write(identifier.strip() + "\n")
# close files
infile.close()
outfile.close()
