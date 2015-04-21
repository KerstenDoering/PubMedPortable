#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Bjoern Gruening <bjoern.gruening@gmail.com>
"""
#Kersten Doering 04.06.2014

#check https://github.com/miracle2k/xappy/blob/master/docs/introduction.rst for nice examples

import xappy
searchConn = xappy.SearchConnection("xapian/xapian2015")
searchConn.reopen()



#########################

querystring = "pancreatic"

q = searchConn.query_field('title',querystring)

print "search query: ", q

#save all machting documents in "results" (starting with rank 0 - check help documentation of function "search")
results = searchConn.search(q, 0, searchConn.get_doccount())

print "number of matches: ", results.matches_estimated

### debug: ###
#print first 5 titles with highlight function and save first 1000 titles in an HTML file
#print "### first 5 hits: ###"
#print "Rank\tPubMed-ID\tTitle (query term highlighted)"
#for index,result in enumerate(results):
#    if "<b>" in results.get_hit(index).highlight('title')[0]:
#        print index, "\t", result.id, "\t", results.get_hit(index).highlight('title')[0]
#    else:
#        print resuld.id, "does not contain a highlighted term"
#        if index > 5:
#            break

#open HTML file
outfile = open("Xapian_query_results.html","w")
#document header
start_string = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head>
<meta http-equiv="content-type" content="text/html; charset=windows-1252">
<title>Xapian_query_results</title>
</head>
<body>

<table border="1" width="100%">
  <tbody><tr>
    <th>Rank</th>
    <th>PubMed-ID</th>
    <th>Title (query term highlighted)</th>
  </tr>
"""
#string for finishing HTML document
end_string = """
</tbody></table>

</body></html>
"""

#write header
outfile.write(start_string)
print "### save first 1000 hits in Xapian_query_results.html ###"
#write the first 1000 PubMed-IDs and titles with term "pancreatic" or stem "pancreat"
for index,result in enumerate(results):
        outfile.write("<tr><td>" + str(index) + "</td><td>" + result.id + "</td><td>" + results.get_hit(index).highlight('title')[0] +"</td></tr>")
        if index == 999:
            break

#write string for finishing HTML document
outfile.write(end_string)
#close file connection
outfile.close()
#close connection to Xapian database
#searchConn.close()
