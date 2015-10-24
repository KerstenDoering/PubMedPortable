#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script processes articles with annotations in tab-separated PubTator format (e.g. from "python call_PubTator.py -i pmid_list.txt -o gene.csv -t Gene -f PubTator").
    |t|\t<title>
    |a|\t<abstract>
    <PubMed ID>\t<begin offset>\t<end offset>\t<synonym>\t<type of entity>\t<type-specific entity identifier>
    ...
    \n
    In the case of the Gene classifier, Entrez genes can be mapped to UniProt IDs (access to sequences) with the GeneID number (http://www.uniprot.org/uploadlists), the Disease identifiers are MeSH identifiers (https://www.nlm.nih.gov/mesh/2011/mesh_browser/MBrowser.html or no ID), and the Chemical classifier provides different IDs (CHEBI, MeSH, or no ID).
    Use the option "-s" to select only synonyms, but not identifiers (e.g. for chemicals or diseases).
"""

# parse parameters given for this script
from optparse import OptionParser

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-i", "--infile", dest="i", help='name of the input file containing all annotated articles in PubTator format (default: gene_complete.csv)', default="gene_complete.csv")
    parser.add_option("-o", "--outfile", dest="o", help='name of the output file containing all PubMed IDs with a normalized synonym (default: pmid_gene_identifier.csv)', default="pmid_gene_identifier.csv")
    parser.add_option("-s","--synonym", dest="s", help='select only synonyms with a type-specific identifier (default=True)', action="store_false", default=True)
    (options, args) = parser.parse_args()
    
    # save parameters in an extra variable
    outfile = options.o
    infile = options.i
    synonyms = options.s

    # read PubTator format and save PubMed ID (as key) with synonym and identifier (as values - list of tuples)
    # select synonyms case-insensitive, use a dictionary with lowered names to check whether a synonym is already inside the list or not
    pmids_entities = {}
    pmids_entities_lower = {}
    # if type-specific identifiers should be selected (default):
    if synonyms:
        f = open(infile,"r")
        for line in f:
            # split for tab characters - only lines with annotations will have more than 1 element afterwards
            temp = line.strip().split("\t")
            # if there are annotations for a PubMed ID
            # condition "equal to 6 splitted terms" to select only lines with type-specific identifier
            if len(temp) == 6:
                # if a PubMed ID is not yet in pmids
                # temp[3] is the synonym, temp[5] is the identifier
                if not temp[0] in pmids_entities:
                    pmids_entities[temp[0]] = [(temp[3],temp[5])]
                    pmids_entities_lower[temp[0]] = [(temp[3].lower(),temp[5])]
                # else if a tuple of synonym and identifier is not yet in the list of tuples for a given PubMed ID, add it
                elif not (temp[3].lower(),temp[5]) in pmids_entities_lower[temp[0]]:
                    pmids_entities[temp[0]].append((temp[3],temp[5]))
                    pmids_entities_lower[temp[0]].append((temp[3].lower(),temp[5]))
        f.close()

        # write PubMed IDs and entities (first synonym, then identifier) tab-separated to file
        f = open(outfile,"w")
        # value is a list of tuples
        for pmid, value in pmids_entities.items():
            # tuples[0] is the synonym, tuples[1] is the identifier
            for tuples in value:
                f.write(pmid + "\t" + tuples[0] + "\t" + tuples[1] + "\n")
        f.close()
    # e.g. in the case of chemicals or diseases, where identifiers are not always provided
    else:
        f = open(infile,"r")
        for line in f:
            # split for tab characters - only lines with annotations will have more than 1 element afterwards
            temp = line.strip().split("\t")
            # if there are annotations for a PubMed ID
            if len(temp) > 1:
                # if a PubMed ID is not yet in pmids
                # temp[3] is the synonym
                if not temp[0] in pmids_entities:
                    pmids_entities[temp[0]] = [temp[3]]
                    pmids_entities_lower[temp[0]] = [temp[3].lower()]
                # else if a tuple of synonym and identifier is not yet in the list of tuples for a given PubMed ID, add it
                elif not temp[3].lower() in pmids_entities_lower[temp[0]]:
                    pmids_entities[temp[0]].append(temp[3])
                    pmids_entities_lower[temp[0]].append(temp[3].lower())
        f.close()

        # write PubMed IDs and entities (first synonym, then identifier) tab-separated to file
        f = open(outfile,"w")
        # value is a list of tuples
        for pmid, value in pmids_entities.items():
            # value is a list of synonyms
            for synonym in value:
                f.write(pmid + "\t" + synonym + "\n")
        f.close()
