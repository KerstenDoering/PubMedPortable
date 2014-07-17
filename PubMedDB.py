#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2014, Bjoern Gruening <bjoern.gruening@gmail.com>, Kersten Doering <kersten.doering@gmail.com>

    This script creates tables in the PostgreSQL schema pubmed. The basic setup of tables and columns is based on:
    http://biotext.berkeley.edu/code/medline-schema/medline-schema-perl-oracle.sql
"""

import sys
import sqlalchemy.types as types
from sqlalchemy import *
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref


"""
    Build tables, classes, and mappings
    http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html
"""


SCHEMA = "pubmed"

Base = declarative_base()

class Citation(Base):
    __tablename__ = "tbl_medline_citation"
    pmid                            = Column(INTEGER, nullable=False, primary_key=True)
    date_created                    = Column(DATE)
    date_completed                  = Column(DATE, index=True)
    date_revised                    = Column(DATE, index=True)
    number_of_references            = Column(Integer, default="0")
    keyword_list_owner              = Column(VARCHAR(30))
    citation_owner                  = Column(VARCHAR(30), default='NLM')
    citation_status                 = Column(VARCHAR(50))
    article_title                   = Column(VARCHAR(4000), nullable=False)
    start_page                      = Column(VARCHAR(10))
    end_page                        = Column(VARCHAR(10))
    medline_pgn                     = Column(VARCHAR(200))
    article_affiliation             = Column(VARCHAR(2000))
    article_author_list_comp_yn     = Column(CHAR(1),default='Y')
    data_bank_list_complete_yn      = Column(CHAR(1),default='Y')
    grant_list_complete_yn          = Column(CHAR(1),default='Y')
    vernacular_title                = Column(VARCHAR(4000))

    def __init__(self):
        self.pmid
        self.date_created
        self.date_completed
        self.date_revised
        self.number_of_references
        self.keyword_list_owner
        self.citation_owner
        self.citation_status
        self.article_title
        self.medline_pgn
        self.article_affiliation
        self.article_author_list_comp_yn
        self.data_bank_list_complete_yn
        self.grant_list_complete_yn
        self.vernacular_title

    def __repr__(self):
        return "Citations: \n\tPMID: %s\n\tArticle Title: %s\n\tCreated: %s\n\tCompleted: %s" % (self.pmid, self.article_title, self.date_created, self.date_completed)

    __table_args__  = (
        CheckConstraint("keyword_list_owner IN ('NLM', 'NASA', 'PIP', 'KIE', 'HSR', 'HMD', 'SIS', 'NOTNLM')", name='ck1_medline_citation'),
        CheckConstraint("citation_owner IN ('NLM', 'NASA', 'PIP', 'KIE', 'HSR', 'HMD', 'SIS', 'NOTNLM')", name='ck2_medline_citation'),
        CheckConstraint("citation_status IN ('In-Data-Review', 'In-Process', 'MEDLINE', 'OLDMEDLINE', 'PubMed-not-MEDLINE', 'Publisher', 'Completed')", name='ck3_medline_citation'),
        CheckConstraint("article_author_list_comp_yn IN ('Y', 'N', 'y', 'n')", name='ck4_medline_citation'),
        CheckConstraint("data_bank_list_complete_yn IN ('Y', 'N', 'y', 'n')", name='ck5_medline_citation'),
        CheckConstraint("grant_list_complete_yn IN ('Y', 'N', 'y', 'n')", name='ck6_medline_citation'),
        {'schema': SCHEMA} 
    )


class PMID_File_Mapping(Base):
    __tablename__ = "tbl_pmids_in_file"

    xml_file_name   = Column(VARCHAR(50), nullable=False)
    fk_pmid            = Column(INTEGER, nullable=False)

    def __init__(self):
        pass
        #self.xml_file_name = xml_file_name
        #self.pmid = pmid

    def __repr__(self):
        pass
        #return "PMID FIle Mapping (%s - %s)" % ()

    __table_args__  = (
        ForeignKeyConstraint(['xml_file_name'], [SCHEMA+'.tbl_xml_file.xml_file_name'], onupdate="CASCADE", ondelete="CASCADE", name='fk1_pmids_in_file'),
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk2_pmids_in_file"),
        PrimaryKeyConstraint('xml_file_name', 'fk_pmid'),
        {'schema': SCHEMA} 
    )


class XMLFile(Base):
    __tablename__ = "tbl_xml_file"

    xml_file_name = Column(VARCHAR(50),    nullable=False, primary_key=True)
    doc_type_name = Column(VARCHAR(100))
    dtd_public_id = Column(VARCHAR(200))#,   nullable=False)
    dtd_system_id = Column(VARCHAR(200))#,   nullable=False)
    time_processed = Column(DateTime())

    def __init__(self):
        self.xml_file_name
        self.doc_type_name# = doc_type_name
        self.dtd_system_id# = dtd_system_id
        self.time_processed

    def __repr__(self):
        return "XMLFile(%s, %s, %s, %s)" % (self.xml_file_name, self.doc_type_name, self.dtd_system_id, self.time_processed)

    citation = relation(Citation, secondary=PMID_File_Mapping.__table__, backref=backref('xml_files', order_by=xml_file_name))

    __table_args__  = (
        {'schema': SCHEMA} 
    )


class Journal(Base):
    __tablename__ = "tbl_journal"

    fk_pmid                = Column(INTEGER, nullable=False, primary_key=True)
    issn                = Column(VARCHAR(30), index=True)
    issn_type           = Column(VARCHAR(30))
    volume              = Column(VARCHAR(200))
    issue               = Column(VARCHAR(200))
    pub_date_year       = Column(Integer(4), index=True)
    pub_date_month      = Column(VARCHAR(20))
    pub_date_day        = Column(VARCHAR(2))
    medline_date        = Column(VARCHAR(40))
    title               = Column(VARCHAR(2000))
    iso_abbreviation    = Column(VARCHAR(100))

    def __init__(self):
        self.issn
        self.issn_type
        self.volume
        self.issue
        self.pub_date_year
        self.pub_date_month
        self.pub_date_day
        self.medline_date
        self.title
        self.iso_abbreviation

    def __repr__(self):
        return "Journal (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.issn, self.issn_type, self.volume, self.issue, self.pub_date_year, self.pub_date_month, self.pub_date_day, self.medline_date, self.title, self.iso_abbreviation)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE"),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('journals', order_by=issn, cascade="all, delete-orphan"))


class JournalInfo(Base):
    __tablename__ = "tbl_medline_journal_info"

    fk_pmid            = Column(INTEGER, nullable=False, primary_key=True)
    nlm_unique_id   = Column(VARCHAR(20), index=True)
    medline_ta      = Column(VARCHAR(200), nullable=False, index=True)
    country         = Column(VARCHAR(50))


    def __init__(self):
        self.nlm_unique_id
        self.medline_ta
        self.country

    def __repr__(self):
        return "JournalInfo (%s, %s, %s)" % (self.nlm_unique_id, self.medline_ta, self.country)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_medline_journal_info"),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('journal_infos', order_by=nlm_unique_id, cascade="all, delete-orphan"))


class Abstract(Base):
    __tablename__ = "tbl_abstract"

    fk_pmid                        = Column(INTEGER, nullable=False)
    abstract_text               = Column(Text)
    copyright_information       = Column(VARCHAR(2000))

    def __init__(self):
        self.abstract_text
        self.copyright_information

    def __repr__(self):
        return "Abstract: (%s) \n\n%s" % (self.copyright_information, self.abstract_text)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_abstract"),
        PrimaryKeyConstraint('fk_pmid'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('abstracts', order_by=fk_pmid, cascade="all, delete-orphan"))


class Chemical(Base):
    __tablename__ = "tbl_chemical"
    fk_pmid                    = Column(INTEGER, nullable=False)
    registry_number         = Column(VARCHAR(20), nullable=False)
    name_of_substance       = Column(VARCHAR(3000), nullable=False, index=True)

    def __init__(self):
        self.registry_number
        self.name_of_substance

    def __repr__(self):
        return "Chemical (%s, %s)" % (self.registry_number, self.name_of_substance)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_chemical_list"),
        PrimaryKeyConstraint('fk_pmid', 'registry_number', 'name_of_substance'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('chemicals', order_by=registry_number, cascade="all, delete-orphan"))


class CitationSubset(Base):
    __tablename__ = "tbl_citation_subset"

    fk_pmid                = Column(INTEGER, nullable=False)
    citation_subset     = Column(VARCHAR(500), nullable=False)

    def __init__(self, citation_subset):
        self.citation_subset = citation_subset

    def __repr__(self):
        return "CitationSubset (%s)" % (self.citation_subset)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_citation_subsets"),
        PrimaryKeyConstraint('fk_pmid', 'citation_subset'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('citation_subsets', order_by=citation_subset, cascade="all, delete-orphan"))


class Comment(Base):
    __tablename__ = "tbl_comments_correction"

    id                      = Column(Integer, primary_key=True)
    fk_pmid                    = Column(INTEGER, nullable=False)
    ref_source              = Column(VARCHAR(4000))
    ref_pmid                = Column(INTEGER)
    note                    = Column(VARCHAR(4000))
    type                    = Column(VARCHAR(30), nullable=False)


    def __init__(self):
        self.ref_source
        self.ref_pmid
        self.note
        self.type = type


    def __repr__(self):
        return "Comment (%s, %s, %s, %s, %s, %s)" % (self.ref_source, self.ref_pmid_or_medlineid, self.ref_pmid, self.ref_medlineid, self.note, self.type)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_comments_corrections"),
        CheckConstraint("type IN ('ErratumIn', 'CommentOn', 'CommentIn', 'ErratumFor', 'PartialRetractionIn', 'PartialRetractionOf', 'RepublishedFrom', 'RepublishedIn', 'RetractionOf', 'RetractionIn', 'UpdateIn', 'UpdateOf', 'SummaryForPatientsIn', 'OriginalReportIn', 'ReprintIn', 'ReprintOf')", name='ck1_comments_correction'),
        #CheckConstraint("ref_pmid_or_medlineid IN ('p', 'm', 'P', 'M')", name='ck2_comments_correction'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('comments', order_by=ref_source, cascade="all, delete-orphan"))


class GeneSymbol(Base):
    __tablename__ = "tbl_gene_symbol"

    fk_pmid            = Column(INTEGER, nullable=False)
    gene_symbol     = Column(VARCHAR(40), nullable=False, index=True) #a bug in one medlin entry causes an increase to 40, from 30


    def __init__(self):
        self.gene_symbol

    def __repr__(self):
        return "GeneSymbol (%s)" % (self.gene_symbol)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_gene_symbol_list"),
        PrimaryKeyConstraint('fk_pmid', 'gene_symbol'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('gene_symbols', order_by=gene_symbol, cascade="all, delete-orphan"))


class MeSHHeading(Base):
    __tablename__ = "tbl_mesh_heading"

    fk_pmid                        = Column(INTEGER, nullable=False)
    descriptor_name             = Column(VARCHAR(500))
    descriptor_name_major_yn    = Column(CHAR(1), default='N')

    def __init__(self):
        self.descriptor_name
        self.descriptor_name_major_yn

    def __repr__(self):
        return "MESH_Headings (%s, %s)" % (self.descriptor_name, self.descriptor_name_major_yn,)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_mesh_heading_list"),
        PrimaryKeyConstraint('fk_pmid', 'descriptor_name'),
        CheckConstraint("descriptor_name_major_yn IN ('Y', 'N', 'y', 'n')", name='ck1_mesh_heading_list'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('meshheadings', order_by=descriptor_name, cascade="all, delete-orphan"))


class Qualifier(Base):
    __tablename__ = "tbl_qualifier_name"

    fk_pmid                        = Column(INTEGER, nullable=False)
    descriptor_name             = Column(VARCHAR(500), index=True)
    qualifier_name              = Column(VARCHAR(500), index=True)
    qualifier_name_major_yn     = Column(CHAR(1), default='N')

    def __init__(self):
        self.descriptor_name
        self.qualifier_name
        self.qualifier_name_major_yn

    def __repr__(self):
        return "Qualifier (%s, %s, %s)" % (self.descriptor_name, self.qualifier_name, self.qualifier_name_major_yn)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_qualifier_names"),
        PrimaryKeyConstraint('fk_pmid', 'descriptor_name', 'qualifier_name'),
        CheckConstraint("qualifier_name_major_yn IN ('Y', 'N', 'y', 'n')", name='ck2_qualifier_names'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('qualifiers', order_by=qualifier_name, cascade="all, delete-orphan"))


class PersonalName(Base):
    __tablename__ = "tbl_personal_name_subject"

    id                  = Column(Integer, primary_key=True)
    fk_pmid                = Column(INTEGER, nullable=False)
    last_name           = Column(VARCHAR(300), nullable=False, index=True)
    fore_name           = Column(VARCHAR(100))
    initials            = Column(VARCHAR(10))
    suffix              = Column(VARCHAR(20))

    def __init__(self):
        self.last_name
        self.fore_name
        self.initials
        self.suffix

    def __repr__(self):
        return "PersonalName (%s, %s, %s, %s)" % (self.last_name, self.fore_name, self.initials, self.suffix)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_personal_name_subject_list"),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('personal_names', order_by=last_name, cascade="all, delete-orphan"))


class Other(Base):
    __tablename__ = "tbl_other_id"

    fk_pmid                = Column(INTEGER, nullable=False)
    other_id            = Column(VARCHAR(30), nullable=False)
    other_id_source     = Column(VARCHAR(20), nullable=False)

    def __init__(self):
        self.other_id
        self.other_id_source

    def __repr__(self):
        return "Other (%s, %s)" % (self.other_id, self.other_id_source)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_other_ids"),
        PrimaryKeyConstraint('fk_pmid', 'other_id', 'other_id_source'),
        CheckConstraint("other_id_source IN ('NASA', 'KIE', 'PIP', 'POP', 'ARPL', 'CPC', 'IND', 'CPFH', 'CLML', 'IM', 'SGC', 'NLM', 'NRCBL', 'QCIM', 'QCICL')", name='ck1_other_ids'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('others', order_by=other_id, cascade="all, delete-orphan"))


class Keyword(Base):
    __tablename__ = "tbl_keyword"

    fk_pmid             = Column(INTEGER, nullable=False)
    keyword             = Column(VARCHAR(500), nullable=False, index=True)
    keyword_major_yn    = Column(CHAR(1), default='N')

    """
    def __init__(self, keyword, keyword_major_yn):
        self.keyword           = keyword
        self.keyword_major_yn    = keyword_major_yn
    """

    def __init__(self):
        self.keyword
        self.keyword_major_yn


    def __repr__(self):
        return "Keyword (%s, %s)" % (self.keyword, self.keyword_major_yn)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_keyword_list"),
        PrimaryKeyConstraint('fk_pmid', 'keyword'),
        CheckConstraint("keyword_major_yn IN ('Y', 'N', 'y', 'n')", name='ck1_keyword_list'),
        {'schema': SCHEMA}
    )

    citation = relation(Citation, backref=backref('keywords', order_by=keyword, cascade="all, delete-orphan"))


class SpaceFlight(Base):
    __tablename__ = "tbl_space_flight_mission"

    fk_pmid                    = Column(INTEGER, nullable=False)
    space_flight_mission    = Column(VARCHAR(500), nullable=False)

    def __init__(self):
        self.space_flight_mission

    def __repr__(self):
        return "SpaceFlight (%s)" % (self.space_flight_mission)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_space_flight_missions"),
        PrimaryKeyConstraint('fk_pmid', 'space_flight_mission'),
        {'schema': SCHEMA}
    )

    citation = relation(Citation, backref=backref('space_flights', order_by=space_flight_mission, cascade="all, delete-orphan"))


class Investigator(Base):
    __tablename__ = "tbl_investigator"

    id                          = Column(Integer, primary_key=True)
    fk_pmid                        = Column(INTEGER, nullable=False)
    last_name                   = Column(VARCHAR(300), index=True)
    fore_name                   = Column(VARCHAR(100))
    initials                    = Column(VARCHAR(10))
    suffix                      = Column(VARCHAR(10))
    investigator_affiliation    = Column(VARCHAR(200))

    def __init__(self):
        self.last_name
        self.fore_name
        self.initials
        self.suffix
        self.investigator_affiliation

    def __repr__(self):
        return "Investigator (%s, %s, %s, %s, %s)" % (self.last_name, self.fore_name, self.initials, self.suffix, self.investigator_affiliation)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_investigator_list"),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('investigators', order_by=last_name, cascade="all, delete-orphan"))


class Notes(Base):
    __tablename__ = "tbl_general_note"

    fk_pmid                = Column(INTEGER, nullable=False)
    general_note        = Column(VARCHAR(2000), nullable=False)
    general_note_owner  = Column(VARCHAR(20))


    def __init__(self):
        self.general_note
        self.general_note_owner


    def __repr__(self):
        return "Keyword (%s, %s)" % (self.general_note, self.general_note_owner)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_general_notes"),
        PrimaryKeyConstraint('fk_pmid', 'general_note'),
        CheckConstraint("general_note_owner IN ('NLM', 'NASA', 'PIP', 'KIE', 'HSR', 'HMD', 'SIS', 'NOTNLM')"),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('notes', order_by=fk_pmid, cascade="all, delete-orphan"))


class Author(Base):
    __tablename__ = "tbl_author"

    id                          = Column(Integer, primary_key=True)
    fk_pmid                        = Column(INTEGER, nullable=False, index=True)
    last_name                   = Column(VARCHAR(300), index=True)
    fore_name                   = Column(VARCHAR(100))
    initials                    = Column(VARCHAR(10))
    suffix                      = Column(VARCHAR(10))
    collective_name             = Column(VARCHAR(2000), index=True)

    """
    def __init__(self, personal_or_collective, last_name, fore_name, first_name, middle_name, initials, suffix, collective_name, author_affiliation):
        self.personal_or_collective = personal_or_collective
        self.last_name              = last_name
        self.fore_name              = fore_name
        self.first_name             = first_name
        self.middle_name            = middle_name
        self.initials               = initials
        self.suffix                 = suffix
        self.collective_name        = collective_name
        self.author_affiliation     = author_affiliation
    """

    def __init__(self):
        self.last_name
        self.fore_name
        self.initials
        self.suffix
        self.collective_name

    def __repr__(self):
        return "Author (%s, %s, %s, %s, %s)" % (self.last_name, self.fore_name, self.initials, self.suffix, self.collective_name)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_author_list"),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('authors', order_by=last_name, cascade="all, delete-orphan"))


class Language(Base):
    __tablename__ = "tbl_language"

    fk_pmid        = Column(INTEGER, nullable=False)
    language    = Column(VARCHAR(50), nullable=False)

    def __init__(self):
        self.language

    def __repr__(self):
        return "Language (%s)" % (self.language)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_languages"),
        PrimaryKeyConstraint('fk_pmid', 'language'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('languages', order_by=language, cascade="all, delete-orphan"))


class DataBank(Base):
    __tablename__ = "tbl_data_bank"

    fk_pmid                = Column(INTEGER, nullable=False)
    data_bank_name      = Column(VARCHAR(300), nullable=False)

    def __init__(self):
        self.data_bank_name

    def __repr__(self):
        return "DataBank (%s)" % (self.data_bank_name)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_data_bank_list"),
        PrimaryKeyConstraint('fk_pmid', 'data_bank_name'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('databanks', order_by=data_bank_name, cascade="all, delete-orphan"))


class Accession(Base):
    __tablename__ = "tbl_accession_number"

    fk_pmid                = Column(INTEGER, nullable=False)
    data_bank_name      = Column(VARCHAR(300), nullable=False, index=True)
    accession_number    = Column(VARCHAR(100), nullable=False, index=True)

    def __init__(self):
        self.data_bank_name
        self.accession_number

    def __repr__(self):
        return "Accession (%s, %s)" % (self.data_bank_name, self.accession_number)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_accession_number_list"),
        PrimaryKeyConstraint('fk_pmid', 'data_bank_name', 'accession_number'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('accessions', order_by=data_bank_name, cascade="all, delete-orphan"))


class Grant(Base):
    __tablename__ = "tbl_grant"

    id              = Column(Integer, primary_key=True)
    fk_pmid            = Column(INTEGER, nullable=False, index=True)
    grantid         = Column(VARCHAR(200), index=True)
    acronym         = Column(VARCHAR(20))
    agency          = Column(VARCHAR(200))
    country          = Column(VARCHAR(200))

    def __init__(self):
        self.grantid
        self.acronym
        self.agency
        self.country

    def __repr__(self):
        return "Grant (%s, %s, %s, %s)" % (self.grantid, self.acronym, self.agency, self.country)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_grant_list"),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('grants', order_by=grantid, cascade="all, delete-orphan"))


class PublicationType(Base):
    __tablename__ = "tbl_publication_type"

    fk_pmid                = Column(INTEGER, nullable=False)
    publication_type    = Column(VARCHAR(200), nullable=False)

    def __init__(self):
        self.publication_type

    def __repr__(self):
        return "PublicationType (%s)" % (self.publication_type)

    __table_args__  = (
        ForeignKeyConstraint(['fk_pmid'], [SCHEMA+'.tbl_medline_citation.pmid'], onupdate="CASCADE", ondelete="CASCADE", name="fk_publication_type_list"),
        PrimaryKeyConstraint('fk_pmid', 'publication_type'),
        {'schema': SCHEMA}
    )
    citation = relation(Citation, backref=backref('publication_types', order_by=publication_type, cascade="all, delete-orphan"))


##old code not used:
#def create_tssearch(engine):
#    """
#        Its currently not possible to set TSVECTOR and TSQUERY column types through SqlAlchemy,
#        so do it ...
#    """

#    Session = sessionmaker(bind=engine)
#    session = Session()
#    connection = session.connection()

#    connection.execute("""CREATE TRIGGER xapianupdate AFTER INSERT ON pubmed.tbl_medline_citation FOR EACH ROW EXECUTE PROCEDURE pubmed.add_to_xapian();""")
#    session.commit()
#    session.close()

#code changed Kersten 13.06.2014
def init(db):
    """
        initialize the database and return the db_engine and the Base-Class for further usage
        an already existing DB want be overridden, you still get the handle (engine) to the DB
    """
    con = 'postgresql://parser:parser@localhost/'+db
    engine = create_engine(con)
    Base.metadata.create_all(engine)

    return engine, Base


#code changed Kersten 13.06.2014
def create_tables(db):
    """
        reset the whole DB
    """
    con = 'postgresql://parser:parser@localhost/'+db
    engine, Base = init(db)
    try:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    except:
        print "Can't create table"
        raise


if __name__ == "__main__":
    #code changed Kersten 13.06.2014
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-d", "--database",
                      dest="database", default="pancreatic_cancer_db",
                      help="What is the name of the database. (Default: pancreatic_cancer_db)")

    (options, args) = parser.parse_args()
    init(options.database)









