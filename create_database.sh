#   Copyright (c) 2014, Kersten Doering <kersten.doering@gmail.com>

#shell script for creating a database with schema pubmed by using xml files from PubMed

################################################################

#example:

#first create database and give access rights to user parser:
#psql template1
#template1=# CREATE DATABASE parserdb;
#CREATE DATABASE
#template1=# GRANT ALL PRIVILEGES ON DATABASE parserdb to parser;
#GRANT
#template1=# \q

#then create tables and load xml data into PostgreSQL database
#usage: ./create_database.sh <path/to/input/files> <optional: database name> <optional: # processors>
#./create_database.sh /media/Databases/kersten/drugmine_cors/streptom/git_removed/Abstracts/xml_pubmed parserdb 4
#

################################################################

#print path for input files provided by user
#-n asks for a non-null/non-zero string variable
if [ -n "$1" ]; then
    path=$1
    echo "path is: $path"
else
    echo "usage: ./create_database.sh <path/to/input/files> <optional: database name> <optional: # processors>"
    exit
fi
#check name of database used - default is pubmed2go
if [ -n "$2" ]; then
    database=$2
else
    database="pancreatic_cancer_db"
fi
echo "name of database is: $database"

#check number of processors that should be used - default is 2
if [ -n "$3" ]; then
    proc=$3
else
    proc=2
fi
echo "number of processors is: $proc"

#ask user to press any key before going on
echo "### all files in schema pubmed will be deleted before new input files will be included in database $database - drop schema pubmed if it is already there ###"
function pause(){
   read -p "$*"
}
pause 'press any key to continue or Ctrl+c to cancel ...'

#if database and user were created as it is described in the documenation, schema pubmed will be created
psql -h localhost -d $database -U parser -f create_schema.sql

#create tables in selected database
echo "create tables in database ..."
python PubMedDB.py -d $database

#how many input files
max=`find $1 | wc -l`

#range of seq only reaches the biggest value below max, but this is not a problem, because 50 is added to -e each time for-loop is called
#max. connections to psql can be a limiting fact, because the ORM engine closes connections sometimes too slow - run subsets of 50 files add sleep command if parser crashes
#call parser with -c: clean db for first set of files, run with 2 processors, process the first 210 files, print parsed files and process IDs:
#echo "number of files to process: $max"

#for loop to proceess 
for i in `seq 0 50 $max`
do
    end=`expr $i + 50`
    if [ "$i" == "0" ]; then
        python PubMedParser.py -i $path -d $database -v -c -p $proc -s $i -e $end
#        sleep 1m
    else
        python PubMedParser.py -i $path -d $database -v -p $proc -s $i -e $end
#        sleep 1m
    fi
done
