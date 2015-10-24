#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script merges the result files from get_years.py. For each Entrez GeneID number, there is a file with the name <identifier>.csv. The gene names are hard-coded. There are three files as output: KRAS.csv, CDKN2A, and BRCA2.csv.
"""

# to join paths
import os

# gene names
names = ["KRAS","BRCA2","CDKN2A"]

# get current path
mypath = os.getcwd()

# dictionary to store a dictionary with results (year and number of abstracts)
names_years ={}

# iterate over gene names
for name in names:
    # change into gene directory
    os.chdir(name)
    # create a new dictionary in the dictioanry names_years
    names_years[name] = {}
    # get all files in the current directory
    files = os.listdir(os.getcwd())
    # iterate over list of files
    for infile in files:
        # open file with years and number of abstracts (comma-separated)
        f = open(infile,"r")
        # iterate over lines in file
        for line in f:
            # split comma-separated line
            temp = line.strip().split(",")
            # if this year was not yet added for the current gene, create it
            if not temp[0] in names_years[name]:
                names_years[name][temp[0]] = int(temp[1])
            # else: sum up the number of abstracts for this year
            else:
                names_years[name][temp[0]] += int(temp[1])
        # close file
        f.close()
    # get all yearas for the current gene
    keys = names_years[name].keys()
    # sort years in descending order
    keys.sort(reverse=True)
    # change back to parent directory
    os.chdir("..")
    # create output file with name <gene>.csv
    outfile = open(name + ".csv","w")
    # iterate over sorted list of years for this gene
    for year in keys:
        # generate comma-separated output (year and number of abstracts)
        outfile.write(year + "," + str(names_years[name][year]) + "\n")
    # close file
    outfile.close()

