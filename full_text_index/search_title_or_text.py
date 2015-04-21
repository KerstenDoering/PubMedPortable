#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>, Bjoern Gruening <bjoern.gruening@gmail.com>
"""
#Kersten Doering 16.06.2014

#check https://github.com/miracle2k/xappy/blob/master/docs/introduction.rst for nice examples

import xappy
searchConn = xappy.SearchConnection("xapian/xapian2015")
searchConn.reopen()



#########################

querystring = "R115777"
#another example:
#querystring = "pancreatic cancer" #also searches for "pancreat" and "cancers"
#use phrase search to get only exact hits

title, text, keyword = querystring, querystring, querystring

title_q = searchConn.query_field('title', title)
text_q = searchConn.query_field('text', text)
#other fields are possible:
#keyword_q = searchConn.query_field('keyword', keyword)

print "search query title: ", title_q
print "search query text: ", text_q
#other fields are possible:
#print "search query keyword: ", keyword_q

merged_q = searchConn.query_composite(searchConn.OP_OR, [title_q, text_q])#, keyword_q])#other fields are possible:
print "merged search query: ", merged_q


#save all machting documents in "results" (starting with rank 0 - check help documentation of function "search")
results = searchConn.search(merged_q, 0, searchConn.get_doccount())

print "number of matches: ", results.matches_estimated

### debug: ###
##print first 5 titles with highlight function and save first 1000 titles in an HTML file
#print "Rank\tPubMed-ID\tTitle (query term highlighted)"
#for index,result in enumerate(results):
#    if index > 4:
#        break
#    try:
#        print "%s\t%s\t%s\t%s" % (result.rank, result.id,results.get_hit(index).highlight('title')[0], results.get_hit(index).highlight('text')[0])
#    except:
#        print "%s\t%s\t%s\t%s" % (result.rank, result.id,results.get_hit(index).highlight('title')[0], "<i>no abstract</i>")


#open HTML file
outfile = open("Xapian_query_results_OR.html","w")
#document header
start_string = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head>
<meta http-equiv="content-type" content="text/html; charset=windows-1252">
<title>Xapian_query_results OR</title>
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
print "### save results in Xapian_query_results_OR.html ###"
for index,result in enumerate(results):
        try:
            outfile.write("<tr><td>" + str(index) + "</td><td>" + result.id + "</td><td>" + results.get_hit(index).highlight('title')[0] +"</td><td>" + results.get_hit(index).highlight('text')[0] + "</td></tr>")
        except:
            outfile.write("<tr><td>" + str(index) + "</td><td>" + result.id + "</td><td>" + results.get_hit(index).highlight('title')[0] +"</td><td>" + "<i>no abstract</i>" + "</td></tr>")

#write string for finishing HTML document
outfile.write(end_string)
#close file connection
outfile.close()
#close connection to Xapian database
#searchConn.close()
