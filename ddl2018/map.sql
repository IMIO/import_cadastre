DROP TABLE IF EXISTS public.map;

CREATE TABLE public.map
(
    capakey character varying(34),
    urbainkey character varying(42),
    daa double precision,
    ord character varying(8),
    pe character varying(424),
    adr1 character varying(250),
    adr2 character varying(250),
    pe2 character varying(2),
    sl1 character varying(74) ,
    prc character varying(24) ,
    na1 character varying(20) ,
    co1 double precision,
    cod1 character varying(4) ,
    ri1 double precision,
    acj character varying(8) ,
    tv character varying(2) ,
    prc2 character varying(2) ,
    cadapli character varying(16)
);

ALTER TABLE map ADD PRIMARY KEY(capakey);

DROP INDEX IF EXISTS public.map_capakey_idx;

CREATE INDEX map_capakey_idx
    ON public.map USING btree
    (capakey );
