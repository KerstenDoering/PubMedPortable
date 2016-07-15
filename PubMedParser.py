#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2014, Bjoern Gruening <bjoern.gruening@gmail.com>, Kersten Doering <kersten.doering@gmail.com>

    This parser reads XML files from PubMed and extracts titles,
    abstracts (no full texts), authors, dates, etc. and directly loads them 
    into the pubmed PostgreSQL database schema (defined in PubMedDB.py).
"""

import sys, os
import xml.etree.cElementTree as etree
import datetime, time
import warnings
import logging
import time

import PubMedDB
from sqlalchemy.orm import *
from sqlalchemy import *
from sqlalchemy.exc import *
import gzip
from multiprocessing import Pool


WARNING_LEVEL = "always" #error, ignore, always, default, module, once
# multiple processes, #processors-1 is optimal!
PROCESSES = 4

warnings.simplefilter(WARNING_LEVEL)

#convert 3 letter code of months to digits for unique publication format
month_code = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}

class MedlineParser:
    #db is a global variable and given to MedlineParser(path,db) in _start_parser(path)
    def __init__(self, filepath,db):
        engine, Base = PubMedDB.init(db)
        Session = sessionmaker(bind=engine)
        self.filepath = filepath
        self.session = Session()


    def _parse(self):
        _file = self.filepath

        """
        a = self.session.query(PubMedDB.XMLFile.xml_file_name).filter_by(xml_file_name = os.path.split(self.filepath)[-1])
        if a.all():
            print self.filepath, 'already in DB'
            return True
        """

        if os.path.splitext(_file)[-1] == ".gz":
            _file = gzip.open(_file, 'rb')

        # get an iterable
        context = etree.iterparse(_file, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)

        # get the root element
        event, root = context.next()

        DBCitation = PubMedDB.Citation()
        DBJournal = PubMedDB.Journal()


        DBXMLFile = PubMedDB.XMLFile()
        DBXMLFile.xml_file_name = os.path.split(self.filepath)[-1]
        DBXMLFile.time_processed = datetime.datetime.now()#time.localtime()

        loop_counter = 0 #to check for memory usage each X loops

        for event, elem in context:

            if event == "end":
                if elem.tag == "MedlineCitation" or elem.tag == "BookDocument":
                    loop_counter += 1
                    #catch KeyError in case there is no Owner or Status attribute before committing DBCitation
                    try:
                        DBCitation.citation_owner = elem.attrib["Owner"]
                    except:
                        pass
                    try:
                        DBCitation.citation_status = elem.attrib["Status"]
                    except:
                        pass
                    DBCitation.journals = [DBJournal]

                    pubmed_id = int(elem.find("PMID").text)
                    DBCitation.pmid = pubmed_id

                    try:
                        same_pmid = self.session.query(PubMedDB.Citation).filter( PubMedDB.Citation.pmid == pubmed_id ).all()
                        # The following condition is only for incremental updates. 

                        """
                        # Implementation that replaces the database entry with the new article from the XML file.
                        if same_pmid: # -> evt. any()
                            same_pmid = same_pmid[0]
                            warnings.warn('\nDoubled Citation found (%s).' % pubmed_id)
                            if not same_pmid.date_revised or same_pmid.date_revised < DBCitation.date_revised:
                                warnings.warn('\nReplace old Citation. Old Citation from %s, new citation from %s.' % (same_pmid.date_revised, DBCitation.date_revised) )
                                self.session.delete( same_pmid )
                                self.session.commit()
                                DBCitation.xml_files = [DBXMLFile] # adds an implicit add()
                                self.session.add( DBCitation )
                        """

                        # Keep database entry that is already saved in database and continue with the next PubMed-ID.
                        # Manually deleting entries is possible (with PGAdmin3 or via command-line), e.g.:
                        # DELETE FROM pubmed.tbl_medline_citation WHERE pmid = 25005691;
                        if same_pmid:
                            print "Article already in database - " + str(same_pmid[0]) + "Continuing with next PubMed-ID"
                            DBCitation = PubMedDB.Citation()
                            DBJournal = PubMedDB.Journal()
                            elem.clear()
                            self.session.commit()
                            continue
                        else:
                            DBCitation.xml_files = [DBXMLFile] # adds an implicit add()
                            self.session.add(DBCitation)

                        if loop_counter % 1000 == 0:
                            self.session.commit()

                    except (IntegrityError) as error:
                        warnings.warn("\nIntegrityError: "+str(error), Warning)
                        self.session.rollback()
                    except Exception as e:
                        warnings.warn("\nUnbekannter Fehler:"+str(e), Warning)
                        self.session.rollback()
                        raise

                    DBCitation = PubMedDB.Citation()
                    DBJournal = PubMedDB.Journal()
                    elem.clear()

                #Kersten: some dates are given in 3-letter code - use dictionary month_code for conversion to digits:
                if elem.tag == "DateCreated":
                    try:
                        date = datetime.date(int(elem.find("Year").text), int(elem.find("Month").text), int(elem.find("Day").text))
                    except:
                        date = datetime.date(int(elem.find("Year").text), int(month_code[elem.find("Month").text]), int(elem.find("Day").text))
                    DBCitation.date_created = date

                if elem.tag == "DateCompleted":
                    try:
                        date = datetime.date(int(elem.find("Year").text), int(elem.find("Month").text), int(elem.find("Day").text))
                    except:
                        date = datetime.date(int(elem.find("Year").text), int(month_code[elem.find("Month").text]), int(elem.find("Day").text))
                    DBCitation.date_completed = date

                if elem.tag == "DateRevised":
                    try:
                        date = datetime.date(int(elem.find("Year").text), int(elem.find("Month").text), int(elem.find("Day").text))
                    except:
                        date = datetime.date(int(elem.find("Year").text), int(month_code[elem.find("Month").text]), int(elem.find("Day").text))
                    DBCitation.date_revised = date

                if elem.tag == "NumberOfReferences":
                    DBCitation.number_of_references = elem.text

                if elem.tag == "ISSN":
                    DBJournal.issn = elem.text
                    DBJournal.issn_type = elem.attrib['IssnType']

                if elem.tag == "JournalIssue" or elem.tag == "Book":
                    if elem.find("Volume") != None:         DBJournal.volume = elem.find("Volume").text
                    if elem.find("Issue") != None:          DBJournal.issue = elem.find("Issue").text

                    #ensure pub_date_year with boolean year:
                    year = False
                    for subelem in elem.find("PubDate"):
                        if subelem.tag == "MedlineDate":
                            if len(subelem.text) > 40:
                                DBJournal.medline_date = subelem.text[:37] + "..."
                            else:
                                DBJournal.medline_date = subelem.text
                        elif subelem.tag == "Year":
                            year = True
                            DBJournal.pub_date_year = subelem.text
                        elif subelem.tag == "Month":
                            if subelem.text in month_code:
                                DBJournal.pub_date_month = month_code[subelem.text]
                            else:
                                DBJournal.pub_date_month = subelem.text
                        elif subelem.tag == "Day":
                            DBJournal.pub_date_day = subelem.text

                    if not year:
                        try:
                            temp_year = DBJournal.medline_date[0:4]
                            DBJournal.pub_date_year = temp_year
                        except:
                            print _file, " not able to cast first 4 letters of medline_date ", temp_year
                
                
                #if there is the attribute ArticleDate, month and day are given
                if elem.tag == "ArticleDate":
                    DBJournal.pub_date_year = elem.find("Year").text
                    DBJournal.pub_date_month = elem.find("Month").text
                    DBJournal.pub_date_day = elem.find("Day").text

                if elem.tag == "Title":
                    """ ToDo """
                    pass

                if elem.tag == "Journal":
                    if elem.find("Title") != None:
                        DBJournal.title = elem.find("Title").text
                    if elem.find("ISOAbbreviation") != None:
                        DBJournal.iso_abbreviation = elem.find("ISOAbbreviation").text

                if elem.tag == "ArticleTitle" or elem.tag == "BookTitle":
                    DBCitation.article_title = elem.text
                if elem.tag == "MedlinePgn":
                    DBCitation.medline_pgn = elem.text

                if elem.tag == "AuthorList":
                    #catch KeyError in case there is no CompleteYN attribute before committing DBCitation
                    try:
                        DBCitation.article_author_list_comp_yn = elem.attrib["CompleteYN"]
                    except:
                        pass

                    DBCitation.authors = []
                    for author in elem:
                        DBAuthor = PubMedDB.Author()

                        if author.find("LastName") != None:
                            DBAuthor.last_name = author.find("LastName").text
                        # Forname is restricted to max 99 characters, but it seems like the None query did not always work - try-except-block
                        try:
                            if author.find("ForeName") != None and not len(author.find("ForeName").text) > 100:
                                DBAuthor.fore_name = author.find("ForeName").text
                            elif author.find("ForeName") != None and len(author.find("ForeName").text) > 100:
                                DBAuthor.fore_name = author.find("ForeName").text[0:97] + "..."
                        except:
                            pass
                        if author.find("Initials") != None:
                            DBAuthor.initials = author.find("Initials").text
                        if author.find("Suffix") != None and not len(author.find("Suffix").text) > 20:
                            DBAuthor.suffix = author.find("Suffix").text
                        elif author.find("Suffix") != None and len(author.find("Suffix").text) > 20:
                            DBAuthor.suffix = author.find("Suffix").text[0:17] + "..."
                        if author.find("CollectiveName") != None:
                            DBAuthor.collective_name = author.find("CollectiveName").text

                        DBCitation.authors.append(DBAuthor)

                if elem.tag == "PersonalNameSubjectList":
                    DBCitation.personal_names = []
                    for pname in elem:
                        DBPersonalName = PubMedDB.PersonalName()

                        if pname.find("LastName") != None:
                            DBPersonalName.last_name = pname.find("LastName").text
                        if pname.find("ForeName") != None:
                            DBPersonalName.fore_name = pname.find("ForeName").text
                        if pname.find("Initials") != None:
                            DBPersonalName.initials = pname.find("Initials").text
                        if pname.find("Suffix") != None:
                            DBPersonalName.suffix = pname.find("Suffix").text

                        DBCitation.personal_names.append(DBPersonalName)


                if elem.tag == "InvestigatorList":
                    DBCitation.investigators = []
                    for investigator in elem:
                        DBInvestigator = PubMedDB.Investigator()

                        if investigator.find("LastName") != None:
                            DBInvestigator.last_name = investigator.find("LastName").text
                        if investigator.find("ForeName") != None:
                            DBInvestigator.fore_name = investigator.find("ForeName").text
                        if investigator.find("Initials") != None:
                            DBInvestigator.initials = investigator.find("Initials").text
                        if investigator.find("Suffix") != None:
                            DBInvestigator.suffix = investigator.find("Suffix").text
                        if investigator.find("Affiliation") != None:
                            DBInvestigator.investigator_affiliation = investigator.find("Affiliation").text

                        DBCitation.investigators.append(DBInvestigator)

                if elem.tag == "SpaceFlightMission":
                    DBSpaceFlight = PubMedDB.SpaceFlight()
                    DBSpaceFlight.space_flight_mission = elem.text
                    DBCitation.space_flights = [DBSpaceFlight]

                if elem.tag == "GeneralNote":
                    DBCitation.notes = []
                    for subelem in elem:
                        DBNote = PubMedDB.Note()
                        DBNote.general_note_owner = elem.attrib["Owner"]
                        DBNote.general_note = subelem.text
                        DBCitation.notes.append(DBNote)

                if elem.tag == "ChemicalList":
                    DBCitation.chemicals = []
                    for chemical in elem:
                        DBChemical = PubMedDB.Chemical()

                        if chemical.find("RegistryNumber") != None:
                            DBChemical.registry_number = chemical.find("RegistryNumber").text
                        if chemical.find("NameOfSubstance") != None:
                            DBChemical.name_of_substance = chemical.find("NameOfSubstance").text
                            DBChemical.substance_ui = chemical.find("NameOfSubstance").attrib['UI']
                        DBCitation.chemicals.append(DBChemical)

                if elem.tag == "GeneSymbolList":
                    DBCitation.gene_symbols = []
                    for genes in elem:
                        DBGeneSymbol = PubMedDB.GeneSymbol()
                        if len(genes.text) < 40:
                            DBGeneSymbol.gene_symbol = genes.text
                        else:
                            DBGeneSymbol.gene_symbol = genes.text[:37] + '...'
                        DBCitation.gene_symbols.append(DBGeneSymbol)

                if elem.tag == "CommentsCorrectionsList":
                    DBCitation.comments = []
                    for comment in elem:
                        DBComment = PubMedDB.Comment()
                        DBComment.ref_type = comment.attrib['RefType']
                        comment_ref_source = comment.find('RefSource')
                        if comment_ref_source != None:
                            DBComment.ref_source = comment_ref_source.text
                        comment_pmid_version = comment.find('PMID')
                        if comment_pmid_version != None:
                            DBComment.pmid_version = comment_pmid_version.text
                        DBCitation.comments.append(DBComment)

                if elem.tag == "MedlineJournalInfo":
                    DBJournalInfo = PubMedDB.JournalInfo()
                    if elem.find("NlmUniqueID") != None:
                        DBJournalInfo.nlm_unique_id = elem.find("NlmUniqueID").text
                    if elem.find("Country") != None:
                        DBJournalInfo.country = elem.find("Country").text
                    """#MedlineTA is just a name for the journal as an abbreviation
                    Abstract with PubMed-ID 21625393 has no MedlineTA attributebut it has to be set in PostgreSQL, that is why "unknown" is inserted instead. There is just a <MedlineTA/> tag and the same information is given in  </JournalIssue> <Title>Biotechnology and bioprocess engineering : BBE</Title>, but this is not (yet) read in this parser -> line 173:
                    """
                    if elem.find("MedlineTA") != None and elem.find("MedlineTA").text == None:
                        DBJournalInfo.medline_ta = "unknown"
                    elif elem.find("MedlineTA") != None:
                        DBJournalInfo.medline_ta = elem.find("MedlineTA").text
                    DBCitation.journal_infos = [DBJournalInfo]

                if elem.tag == "CitationSubset":
                    DBCitation.citation_subsets = []
                    for subelem in elem:
                        DBCitationSubset = CitationSubset(subelem.text)
                        DBCitation.citation_subsets.append(DBCitationSubset)

                if elem.tag == "MeshHeadingList":
                    DBCitation.meshheadings = []
                    DBCitation.qualifiers = []
                    for mesh in elem:
                        DBMeSHHeading = PubMedDB.MeSHHeading()
                        mesh_desc = mesh.find("DescriptorName")
                        if mesh_desc != None:
                            DBMeSHHeading.descriptor_name = mesh_desc.text
                            DBMeSHHeading.descriptor_name_major_yn = mesh_desc.attrib['MajorTopicYN']
                            DBMeSHHeading.descriptor_ui = mesh_desc.attrib['UI']
                        if mesh.find("QualifierName") != None:
                            mesh_quals = mesh.findall("QualifierName")
                            for qual in mesh_quals:
                                DBQualifier = PubMedDB.Qualifier()
                                DBQualifier.descriptor_name = mesh_desc.text
                                DBQualifier.qualifier_name = qual.text
                                DBQualifier.qualifier_name_major_yn = qual.attrib['MajorTopicYN']
                                DBQualifier.qualifier_ui = qual.attrib['UI']
                                DBCitation.qualifiers.append(DBQualifier)
                        DBCitation.meshheadings.append(DBMeSHHeading)

                if elem.tag == "GrantList":
                    #catch KeyError in case there is no CompleteYN attribute before committing DBCitation
                    try:
                        DBCitation.grant_list_complete_yn = elem.attrib["CompleteYN"]
                    except:
                        pass
                    DBCitation.grants = []
                    for grant in elem:
                        DBGrants = PubMedDB.Grant()

                        if grant.find("GrantID") != None:
                            DBGrants.grantid = grant.find("GrantID").text
                        if grant.find("Acronym") != None:
                            DBGrants.acronym = grant.find("Acronym").text
                        if grant.find("Agency") != None:
                            DBGrants.agency = grant.find("Agency").text
                        if grant.find("Country") != None:
                            DBGrants.country = grant.find("Country").text
                        DBCitation.grants.append(DBGrants)

                if elem.tag == "DataBankList":
                    #catch KeyError in case there is no CompleteYN attribute before committing DBCitation
                    try:
                        DBCitation.data_bank_list_complete_yn = elem.attrib["CompleteYN"]
                    except:
                        pass
                    DBCitation.accessions = []
                    DBCitation.databanks = []

                    for databank in elem:
                        DBDataBank = PubMedDB.DataBank()
                        DBDataBank.data_bank_name = databank.find("DataBankName").text
                        DBCitation.databanks.append(DBDataBank)

                        acc_numbers = databank.find("AccessionNumberList")
                        if acc_numbers != None:
                            for acc_number in acc_numbers:
                                DBAccession = PubMedDB.Accession()
                                DBAccession.data_bank_name = DBDataBank.data_bank_name
                                DBAccession.accession_number = acc_number.text
                                DBCitation.accessions.append(DBAccession)

                if elem.tag == "Language":
                    DBLanguage = PubMedDB.Language()
                    DBLanguage.language = elem.text
                    DBCitation.languages = [DBLanguage]

                if elem.tag == "PublicationTypeList":
                    DBCitation.publication_types = []
                    for subelem in elem:
                        DBPublicationType = PubMedDB.PublicationType()
                        DBPublicationType.publication_type = subelem.text
                        DBCitation.publication_types.append(DBPublicationType)

                if elem.tag == "Article":
                    #ToDo
                    """
                    for subelem in elem:
                        if subelem.tag == "Journal":
                            for sub_subelem in subelem:
                                pass
                        if subelem.tag == "JArticleTitle":
                            pass
                        if subelem.tag == "JPagination":
                            pass
                        if subelem.tag == "JLanguage":
                            pass
                        if subelem.tag == "JPublicationTypeList":
                            pass
                    """

                if elem.tag == "VernacularTitle":
                    DBCitation.vernacular_title = elem.tag

                if elem.tag == "OtherAbstract":
                    DBOtherAbstract = PubMedDB.OtherAbstract()
                    DBCitation.other_abstracts = []
                    for other in elem:
                        if other.tag == "AbstractText":
                             DBOtherAbstract.other_abstract = other.text
                    DBCitation.other_abstracts.append(DBOtherAbstract)

                if elem.tag == "OtherID":
                    DBCitation.other_ids = []
                    DBOtherID = PubMedDB.OtherID()
                    if len(elem.text) < 80:
                        DBOtherID.other_id = elem.text
                    else:
                        DBOtherID.other_id = elem.text[0:77] + "..."
                    DBOtherID.other_id_source = elem.attrib['Source']
                    DBCitation.other_ids.append(DBOtherID)

                # start Kersten: some abstracts contain another structure - code changed:
                # check for different labels: "OBJECTIVE", "CASE SUMMARY", ...
                # next 3 lines are unchanged
                if elem.tag == "Abstract":
                    DBAbstract = PubMedDB.Abstract()
                    DBCitation.abstracts = []
                    #prepare empty string for "normal" abstracts or "labelled" abstracts
                    temp_abstract_text = ""
                    #if there are multiple AbstractText-Tags:
                    if elem.find("AbstractText") != None and len(elem.findall("AbstractText")) > 1:
                        for child_AbstractText in elem.getchildren():
                            # iteration over all labels is needed otherwise only "OBJECTIVE" would be pushed into database
                            # debug: check label
                            # [('NlmCategory', 'METHODS'), ('Label', 'CASE SUMMARY')]
                            # ...
                            # also checked for empty child-tags in this structure!
                            if child_AbstractText.tag == "AbstractText" and child_AbstractText.text != None:
                            #if child_AbstractText.tag == "AbstractText": # would give an error!
                                # no label - this case should not happen with multiple AbstractText-Tags:
                                if len(child_AbstractText.items()) == 0:
                                    temp_abstract_text +=child_AbstractText.text + "\n"
                                # one label or the NlmCategory - first index has to be zero:
                                if len(child_AbstractText.items()) == 1:
                                    # filter for the wrong label "UNLABELLED" - usually contains the text "ABSTRACT: - not used: 
                                    if child_AbstractText.items()[0][1] == "UNLABELLED":
                                        temp_abstract_text += child_AbstractText.text + "\n"
                                    else:
                                        temp_abstract_text += child_AbstractText.items()[0][1] + ":\n" + child_AbstractText.text + "\n"
                                # label and NlmCategory - take label - first index has to be one:
                                if len(child_AbstractText.items()) == 2:
                                    temp_abstract_text += child_AbstractText.items()[1][1] + ":\n" + child_AbstractText.text + "\n"    
                    # if there is only one AbstractText-Tag ("usually") - no labels used:
                    if elem.find("AbstractText") != None and len(elem.findall("AbstractText")) == 1:
                        temp_abstract_text = elem.findtext("AbstractText")
                    # append abstract text for later pushing it into db:
                    DBAbstract.abstract_text = temp_abstract_text
                    # next 3 lines are unchanged - some abstract texts (few) contain the child-tag "CopyrightInformation" after all AbstractText-Tags:
                    if elem.find("CopyrightInformation") != None:   
                        DBAbstract.copyright_information = elem.find("CopyrightInformation").text
                    DBCitation.abstracts.append(DBAbstract)
                # end Kersten - code changed
                
                """
                #old code:
                if elem.tag == "Abstract":
                    DBAbstract = PubMedDB.Abstract()
                    DBCitation.abstracts = []

                    if elem.find("AbstractText") != None:   DBAbstract.abstract_text = elem.find("AbstractText").text
                    if elem.find("CopyrightInformation") != None:   DBAbstract.copyright_information = elem.find("CopyrightInformation").text
                    DBCitation.abstracts.append(DBAbstract)
                """
                if elem.tag == "KeywordList":
                    #catch KeyError in case there is no Owner attribute before committing DBCitation
                    try:
                        DBCitation.keyword_list_owner = elem.attrib["Owner"]
                    except:
                        pass
                    DBCitation.keywords = []
                    all_keywords = []
                    for subelem in elem:
                        #some documents contain duplicate keywords which would lead to a key error - if-clause
                        if not subelem.text in all_keywords:
                            all_keywords.append(subelem.text)
                        else:
                            continue
                        DBKeyword = PubMedDB.Keyword()
                        DBKeyword.keyword = subelem.text
                        #catch KeyError in case there is no MajorTopicYN attribute before committing DBCitation
                        try:
                            DBKeyword.keyword_major_yn = subelem.attrib["MajorTopicYN"]
                        except:
                            pass
                        DBCitation.keywords.append(DBKeyword)

                if elem.tag == "Affiliation":
                    DBCitation.article_affiliation = elem.text

                if elem.tag == "SupplMeshList":
                    DBCitation.suppl_mesh_names = []
                    for suppl_mesh in elem:
                        DBSupplMeshName = PubMedDB.SupplMeshName()
                        DBSupplMeshName.suppl_mesh_name = suppl_mesh.text
                        DBSupplMeshName.suppl_mesh_name_ui = suppl_mesh.attrib['UI']
                        DBSupplMeshName.suppl_mesh_name_type = suppl_mesh.attrib['Type']
                        DBCitation.suppl_mesh_names.append(DBSupplMeshName)

        self.session.commit()
        return True


def get_memory_usage(pid=os.getpid(), format="%mem"):
    """
        Get the Memory Usage from a specific process
        @pid = Process ID
        @format = % or kb (%mem or rss) ...
    """
    return float(os.popen('ps -p %d -o %s | tail -1' %
                        (pid, format)).read().strip())


def _start_parser(path):
    """
        Used to start MultiProcessor Parsing
    """
    print path, '\tpid:', os.getpid()
    p = MedlineParser(path,db)
    s = p._parse()
    return path

#uses global variable "db" because of result.get()
def run(medline_path, clean, start, end, PROCESSES):
    con = 'postgresql://parser:parser@localhost/'+db

    if end != None:
        end = int(end)

    if clean:
        PubMedDB.create_tables(db)
    
    PubMedDB.init(db)

    paths = []
    for root, dirs, files in os.walk(medline_path):
        for filename in files:
            if os.path.splitext(filename)[-1] in [".xml", ".gz"]:
                paths.append(os.path.join(root,filename))

    paths.sort()
    

    pool = Pool(processes=PROCESSES)    # start with processors
    print "Initialized with ", PROCESSES, "processes"
    #result.get() needs global variable db now - that is why a line "db = options.database" is added in "__main__" - the variable db cannot be given to __start_parser in map_async()
    result = pool.map_async(_start_parser, paths[start:end])
    res = result.get()
    #without multiprocessing:
    #for path in paths:
    #    _start_parser(path)

    print "######################"
    print "###### Finished ######"
    print "######################"


if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-c", "--no_cleaning", dest="clean",
                      action="store_false", default=True,
                      help="Truncate the Database before running the parser (default: True).")
    parser.add_option("-s", "--start",
                      dest="start", default=0,
                      help="All queued files are passed if no start and end parameter is set. Otherwise you can specify a start and end o the queue. For example to split the parsing on several machines.")
    parser.add_option("-e", "--end",
                      dest="end", default=None,
                      help="All queued files are passed if no start and end parameter is set. Otherwise you can specify a start and end o the queue. For example to split the parsing on several machines.")
    parser.add_option("-i", "--input", dest="medline_path",
                      default='data/pancreatic_cancer/',
                      help="specify the path to the medine XML-Files (default: data/pancreatic_cancer/)")
    parser.add_option("-p", "--processes",
                      dest="PROCESSES", default=2,
                      help="How many processes should be used. (Default: 2)")
    parser.add_option("-d", "--database",
                      dest="database", default="pancreatic_cancer_db",
                      help="What is the name of the database. (Default: pancreatic_cancer_db)")

    (options, args) = parser.parse_args()
    db = options.database
    #log start time of programme:
    start = time.asctime()
    run(options.medline_path, options.clean, int(options.start), options.end, int(options.PROCESSES))
    #end time programme 
    end = time.asctime()

    print "programme started - " + start
    print "programme ended - " + end
