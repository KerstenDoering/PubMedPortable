#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script reads a tab-separated file with <PubMed ID>\t<synonym>\t<identifier> and groups the hits by identifiers instead of using the different synonyms per identifier and abstract.
    The output is a sorted list of triples with <synonym>\t<number of abstracts>\t<identifier>.
"""

# parse parameters given for this script
from optparse import OptionParser

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-i", "--infile", dest="i", help='name of the input file containing all annotations from PubTator (default: entities_formatted_identifiers.csv)', default="entities_formatted_identifiers.csv")
    parser.add_option("-o", "--outfile", dest="o", help='name of the output file with unified hits per identifier (default: entities_formatted_identifiers_unified.csv)', default="entities_formatted_identifiers_unified.csv")
    (options, args) = parser.parse_args()

    # save parameters in an extra variable
    outfile = options.o
    infile = options.i

    identifier_pmids = {}
    identifier_synonym = {}
    # read input file:
    f = open(infile,"r")
    for line in f:
        # temp[0]:PubMed ID, temp[1]: synonym, temp[2]: identifier
        temp = line.strip().split("\t")
        # if identifier is not yet stored in dictionary, add it with a one-element list containing the PubMed ID
        # take this synonym as representative for all following synonyms of this identifier
        if not temp[2] in identifier_pmids:
            identifier_pmids[temp[2]] = [temp[0]]
            identifier_synonym[temp[2]] = temp[1]
        # else if this PubMed ID is not yet stored, add it for the given identifier
        elif not temp[0] in identifier_pmids[temp[2]]:
            identifier_pmids[temp[2]].append(temp[0])
    # close input file
    f.close()

    # add all triples (<number of abstracts>\t<synonym>\t<identifier>) and sort them
    hits_identifier_synonym = []
    for identifier, pmids in identifier_pmids.items():
        hits_identifier_synonym.append((len(pmids),identifier_synonym[identifier],identifier))
    hits_identifier_synonym.sort(reverse=True)
    # open output file
    f = open(outfile,"w")
    # save synonym in first column, number of hits in second column and identifier in third column, as provided by the sorted list hits_identifier_synonym
    for triple in hits_identifier_synonym:
        f.write(triple[1] + "\t" + str(triple[0]) + "\t" + triple[2] + "\n")
    # close output file
    f.close()
