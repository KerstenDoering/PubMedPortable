#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Bjoern Gruening <bjoern.gruening@gmail.com>
"""
#Kersten Doering 17.06.2014

#check http://xapian.org/docs/queryparser.html for syntax and functions

import xappy

conn = xappy.SearchConnection("xapian/xapian2015")
conn.reopen()


queryString = "pancreatic colon lung ovarian"

terms = queryString.split(' ')

#if only one term is given, normal search in title and text field is done
if len(terms) > 1:
    #the second term is excluded with "AND NOT"
    title = ' AND NOT '.join(terms)
    title = "R115777 AND " + title
    #another example
#    title = "Erlotinib AND " + title

    text = ' AND NOT '.join(terms)
    text = "R115777 AND " + text
    #another example
#    text = "Erlotinib AND " + text
else:
    title, text = queryString, queryString



title_q = conn.query_field('title', title)
text_q = conn.query_field('text', text)

#merge the two NOT-queries for title and text with OR, meaning this should be the case in the title OR the text field
merged_q = conn.query_composite(conn.OP_OR, [title_q, text_q])
print "merged search query: ", merged_q

#save all machting documents in "results" (starting with rank 0 - check help documentation of function "search")
results = conn.search(merged_q, 0, conn.get_doccount())

print "number of matches: ", results.matches_estimated

### debug: ###
##print first 5 examples
#print "Rank\tPubMed-ID\tTitle (query term highlighted)"
#for index, result in enumerate(results):
#    if index > 4:
#        break
#    try:
#        print "%s\t%s\t%s\t%s" % (result.rank, result.id,results.get_hit(index).highlight('title')[0], results.get_hit(index).highlight('text')[0])
#    except:
#        print "%s\t%s\t%s\t%s" % (result.rank, result.id,results.get_hit(index).highlight('title')[0], "<i>no abstract</i>")


#HTML output:
#open HTML file
outfile = open("Xapian_query_results_NOT.html","w")
#document header
start_string = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head>
<meta http-equiv="content-type" content="text/html; charset=windows-1252">
<title>Xapian_query_results_NOT</title>
</head>
<body>

<table border="1" width="100%">
  <tbody><tr>
    <th>Rank</th>
    <th>PubMed-ID</th>
    <th>Title (query term highlighted)</th>
    <th>Abstract (query term highlighted)</th>
  </tr>
"""
#string for finishing HTML document
end_string = """
</tbody></table>

</body></html>
"""

#write header
outfile.write(start_string)
print "### save results in Xapian_query_results_NOT.html ###"
#write the first 1000 PubMed-IDs and titles with term "pancreatic" or stem "pancreat"
for index,result in enumerate(results):
        try:
            outfile.write("<tr><td>" + str(index) + "</td><td>" + result.id + "</td><td>" + results.get_hit(index).highlight('title')[0] +"</td><td>" + results.get_hit(index).highlight('text')[0] + "</td></tr>")
        except:
            outfile.write("<tr><td>" + str(index) + "</td><td>" + result.id + "</td><td>" + results.get_hit(index).highlight('title')[0] +"</td><td>" + "<i>no abstract</i>" + "</td></tr>")
#        if index > 1000:
#            break

#write string for finishing HTML document
outfile.write(end_string)
#close file connection
outfile.close()
#close connection to Xapian database


#searchConn.close()
