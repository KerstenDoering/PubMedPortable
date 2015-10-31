#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>

    This script generates a bar chart with three columns showing the timelines from the files provided by the script get_years.py (default). The script get_years.py sends a query to the PubMedPortable PostgreSQL database. Using the parameter "-p" replaces the processing of the input from get_years.py with a data set based on the whole PubMed. The provided CSV files can be downloaded by clicking on the bar chart appearing after browser search on http://www.ncbi.nlm.nih.gov/pubmed (15th June 2015).
"""

#show multiple bars?
#http://stackoverflow.com/questions/14270391/python-matplotlib-multiple-bars

# Kersten Doering 11.06.2015

# plot library
import matplotlib.pyplot as plt
# to use command-line parameters
from optparse import OptionParser

# main
if __name__=="__main__":
    parser = OptionParser()
    
    parser.add_option("-p", "--pubmed", dest="p", action="store_true", help='use CSV files from PubMed (default: False)',default = False)
    (options, args) = parser.parse_args()
    pubmed = options.p

    # open files with timelines for search terms
    if pubmed:
        infile = open("KRAS_pubmed.csv","r")
        infile2 = open("BRCA2_pubmed.csv","r")
        infile3 = open("CDKN2A_pubmed.csv","r")
    else:
        infile = open("KRAS.csv","r")
        infile2 = open("CDKN2A.csv","r")
        infile3 = open("BRCA2.csv","r")


    # prepare data for the first search term (KRAS) 
    bins = []
    data = []
    for line in infile:
    #    temp = line.strip().split("\t")
        temp = line.strip().split(",")
        data.append(int(temp[0])-0.3)
        bins.append(int(temp[1]))

    # prepare data for the second search term (BRCA2)
    data_2 = []
    bins_2 = []
    for line in infile2:
    #    temp = line.strip().split("\t")
        temp = line.strip().split(",")
        data_2.append(int(temp[0]))
        bins_2.append(int(temp[1]))

    # prepare data for the third search term (CDKN2A)
    data_3 = []
    bins_3 = []
    for line in infile3:
    #    temp = line.strip().split("\t")
        temp = line.strip().split(",")
        data_3.append(int(temp[0])+0.3)
        bins_3.append(int(temp[1]))

    # figure environment
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # limit range of x-axis and y-axis
    #plt.ylim(0,100)
    plt.xlim(1985,2015)

    # year 2015 cannot be considered as a complete year - delete this bar
    # all three cases refer to the year 2015
    # the number can be understood as a position on the x-axis
    if 2014.7 in data:
        del(data[0])
        del(bins[0])
    if 2015 in data_2:
        del(data_2[0])
        del(bins_2[0])
    if 2015.3 in data_3:
        del(data_3[0])
        del(bins_3[0])

    #shift positions of two bars to the left and to the right by 0.3
    w = 0.3

    # plot the three bars and add a legend
    p1 = ax.bar(data, bins,width=w, color='orange',align='center')
    p2 = ax.bar(data_2, bins_2 ,width=w, color='green',align='center')
    p3 = ax.bar(data_3, bins_3 ,width=w, color='blue',align='center')
    ax.legend((p1[0],p2[2],p3[0]),("KRAS","CDKN2A","BRCA2"),loc=2)

    # add lables for x-axis and y-axis
    plt.ylabel("No. of Publications")
    plt.xlabel("Year of Publication")

    # add title
    if pubmed:
        plt.title("PubMed Data Set")
    else:
        plt.title("Pancreatic Cancer Data Set")

    # save figure
    if pubmed:
        plt.savefig("KRAS_BRCA2_CDKN2A_pubmed.png")
    else:
        plt.savefig("KRAS_CDKN2A_BRCA2.png")

    # show plot on screen
    #plt.show()

    # close files
    infile.close()
    infile2.close()
    infile3.close()


