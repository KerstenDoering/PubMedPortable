#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Bjoern Gruening <bjoern.gruening@gmail.com>
"""
#Kersten Doering 16.06.2014

#check http://xapian.org/docs/queryparser.html for syntax and functions

import xappy
searchConn = xappy.SearchConnection("xapian/xapian2015")
searchConn.reopen()

#########################

querystring1 = "pancreatic cancer"
querystring2 = "Erlotinib"

#in the following example, "pancreatic cancer" and "Erlotinib" are not allowed to have more than 4 other words between them"
#"title" and "text" are searched with Xapian

#"pancreatic cancer" is split into two terms and connected with the other query using "NEAR"
terms = querystring1.split(' ')
querystring1 = " NEAR/3 ".join(terms)#not more than 2 words are allowed to be between "pancreatic" and "cancer"

#NEAR searches without considering the word order, while in case of ADJ the word order is fixed
title = querystring1 + " NEAR/5 " + querystring2#adjusting the limit of words between the terms changes the results

#same query can be done for the field "text" which is the PubMed abstract and both query fields can be connected with logical OR - look at search_title_or_text.py or search_not_title_or_text.py
#notice that this becomes a phrase search now for the single terms
title_q = searchConn.query_field('title', title)


print "search query: ", title_q

#save all machting documents in "results" (starting with rank 0 - check help documentation of function "search")
results = searchConn.search(title_q, 0, searchConn.get_doccount())

print "number of matches: ", results.matches_estimated
### debug: ###
#print "Rank\tPubMed-ID\tTitle (query term highlighted)"
#for index,result in enumerate(results):
#    if "<b>" in results.get_hit(index).highlight('title')[0]:
#        print index, "\t", result.id, "\t", results.get_hit(index).highlight('title')[0]
#    else:
#        print resuld.id, "does not contain a highlighted term"
##        if index > 5:
##            break

#HTML output:
#open HTML file
outfile = open("Xapian_query_results_NEAR.html","w")
#document header
start_string = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head>
<meta http-equiv="content-type" content="text/html; charset=windows-1252">
<title>Xapian_query_results_NEAR</title>
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
print "### save results in Xapian_query_results_NEAR.html ###"
#write the first 1000 PubMed-IDs and titles with term "pancreatic" or stem "pancreat"
for index,result in enumerate(results):
        outfile.write("<tr><td>" + str(index) + "</td><td>" + result.id + "</td><td>" + results.get_hit(index).highlight('title')[0] +"</td></tr>")
#        if index == 999:
#            break

#write string for finishing HTML document
outfile.write(end_string)
#close file connection
outfile.close()
#close connection to Xapian database


#searchConn.close()
