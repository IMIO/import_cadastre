-- Table: public.toli

DROP TABLE IF EXISTS public.toli;

DROP SEQUENCE IF EXISTS public.toli_gid_seq;

CREATE SEQUENCE public.toli_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.toli
(
    gid integer NOT NULL DEFAULT nextval('toli_gid_seq'),
    tolity character varying(2),
    tolitx character varying(254),
    sheet character varying(18),
    the_geom geometry,
    CONSTRAINT toli_pkey PRIMARY KEY (gid),
    CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    --CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'MULTILINESTRING'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);

-- Index: toli_pk_idx

DROP INDEX IF EXISTS public.toli_pk_idx;

CREATE UNIQUE INDEX toli_pk_idx
    ON public.toli USING btree
    (gid);

-- Index: toli_the_geom_gist

DROP INDEX IF EXISTS public.toli_the_geom_gist;

CREATE INDEX toli_the_geom_gist
    ON public.toli USING gist
    (the_geom);

-- Index: tolity_idx

DROP INDEX IF EXISTS public.tolity_idx;

CREATE INDEX tolity_idx
    ON public.toli USING btree
    (tolity);
