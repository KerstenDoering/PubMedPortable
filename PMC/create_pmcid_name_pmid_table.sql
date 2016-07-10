CREATE TABLE tbl_pmcid_name_pmid
(
  pmcid VARCHAR(15) NOT NULL,
  name TEXT NOT NULL,
  pmid INTEGER,
  CONSTRAINT pmcid_pkey_tbl_pmcid_name_pmid PRIMARY KEY (pmcid)
);

CREATE INDEX name_ix_tbl_pmcid_name_pmid
  ON tbl_pmcid_name_pmid
  USING btree
  (name);

CREATE INDEX pmid_ix_tbl_pmcid_name_pmid
  ON tbl_pmcid_name_pmid
  USING btree
  (pmid);

