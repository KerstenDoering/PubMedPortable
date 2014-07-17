Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>

In this directory, a full text index database folder will be created by "RunXapian.py" as it is described in "Readme.html".
Check the examples "search_title.py", "search_near_title.py", "search_title_or_text.py", and "search_not_title_or_text.py" to see how to query and connect to Xapian.
Have a look at "PubMedXapian.py" to understand which fields are indexed and how this is done with "Xappy". "Article.py" selects all required data from the PostgreSQL database and "SynonymParser.py" executes the function "findPMIDsWithSynonyms()" from "PubMedXapian.py".
