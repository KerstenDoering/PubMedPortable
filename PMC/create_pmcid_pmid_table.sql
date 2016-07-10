CREATE TABLE tbl_pmcid_pmid
(
  pmcid VARCHAR(15) NOT NULL,
  pmid INTEGER,
  CONSTRAINT pmc_pkey_tbl_pmcid_pmid PRIMARY KEY (pmcid)
);

CREATE INDEX pmid_ix_tbl_pmcid_pmid
  ON tbl_pmcid_pmid
  USING btree
  (pmid);

