#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Copyright (c) 2015, Kersten Doering <kersten.doering@gmail.com>
"""

# import modules
# path options
import os

# get all indexing directories from ids.txt and prepare compact command
command = "xapian-compact -m "
ids = []
infile = open("ids.txt","r")
for line in infile:
    # example:
    # 
    temp = line.strip().split("\t")
    # the xapian folders are 0-indexed, but the mapping in ids.txt is 1-indexed
    index = int(temp[0]) - 1
    # add folder id to compact command (with system-dependent path separator)
    command += "xapian" + os.path.sep + str(index) + " "
# add directory name which will contain the fully merged Xapian index
command += "xapian_PMC_complete"

# execute xapian-compact command
print command
os.system(command)
