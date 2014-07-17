#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#Kersten Doering 09.07.2014

if __name__=="__main__":

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-s", "--size", dest="s", help='block size of PubMed-IDs for one XML file', default=100)
    parser.add_option("-f", "--file", dest="f", help="name of the input file with a list of PubMed-IDs", default = "pubmed_result.txt")
    parser.add_option("-d", "--directory", dest="d", help="name of the directory in which the files should be saved", default = "pancreatic_cancer")
    
    (options, args) = parser.parse_args()
    
    #save parameters in an extra variable
    block_size = int(options.s)
    file_name = options.f
    directory_name = options.d


    #get PubMed-IDs, e.g. from browser download
    pmids = []
    infile = open(file_name,"r")
    for zeile in infile:
        pmids.append(zeile.strip())    
    infile.close()
    pmids.sort()

    #save PubMed-ID after PubMed-ID until 100 is reached, then start with the next round
    pmid_100 = []
    #save all commands with 100 PubMed-IDs
    command_list = []
    #use a counter to enumerate file names
    counter = 0
    #give directory path "pancreatic_cancer" as later all files in a directory will be parsed
    #change this parameter to a name related to your database
    for index in range(len(pmids)):
        if len(pmid_100) == block_size:
            if counter < 10:
                file_number = "0000000" + str(counter)
            elif counter < 100:
                file_number = "000000" + str(counter) 
            elif counter < 1000:
                file_number = "00000" + str(counter)
            elif counter < 10000:
                file_number = "0000" + str(counter)
            elif counter < 100000:
                file_number = "000" + str(counter)
            elif counter < 1000000:
                file_number = "00" + str(counter)
            elif counter < 10000000:
                file_number = "0" + str(counter)
            else:
                file_number = "" + str(counter)
            command = "wget -O " + directory_name + "/medline_" + file_number + ".xml \"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" + str(pmid_100).replace("'","").replace("[","").replace("]","").replace(" ","") + "&retmode=xml\"\n"
            counter += 1
            pmid_100 =[]
            command_list.append(command)
        pmid_100.append(int(pmids[index]))


    #for the last run, the 100 probably will not be reached - repeat the appending step one last time
    if counter < 10:
        file_number = "0000000" + str(counter)
    elif counter < 100:
        file_number = "000000" + str(counter) 
    elif counter < 1000:
        file_number = "00000" + str(counter)
    elif counter < 10000:
        file_number = "0000" + str(counter)
    elif counter < 100000:
        file_number = "000" + str(counter)
    elif counter < 1000000:
        file_number = "00" + str(counter)
    elif counter < 10000000:
        file_number = "0" + str(counter)
    else:
        file_number = "" + str(counter)
    command = "wget -O " + directory_name + "/medline_" + str(file_number) + ".xml \"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" + str(pmid_100).replace("'","").replace("[","").replace("]","").replace(" ","") + "&retmode=xml\"\n"
    command_list.append(command)


    #debug: control correct number of written PubMed-IDs
    """
    print command
    print len(pmid_100)
    print counter
    print pmids[-3:]
    print command_list[0]
    print pmids[0:4]
    """

    #write a shell file to execute all wget-EFetch commands
    wget_file = open("efetch.sh", "w")
    for command in command_list:
        wget_file.write(command)
    wget_file.close()

