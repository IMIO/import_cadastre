-- Table: public.inli

DROP TABLE IF EXISTS public.inli;

DROP SEQUENCE IF EXISTS public.inli_gid_seq;

CREATE SEQUENCE public.inli_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.inli
(
    gid integer NOT NULL DEFAULT nextval('inli_gid_seq'),
    inlity character varying(2),
    inlitx character varying(100),
    sheet character varying(18),
    the_geom geometry,
    CONSTRAINT inli_pkey PRIMARY KEY (gid),
    CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    --CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'MULTILINESTRING'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);

-- Index: inli_pk_idx

DROP INDEX IF EXISTS public.inli_pk_idx;

CREATE UNIQUE INDEX inli_pk_idx
    ON public.inli USING btree
    (gid);

-- Index: inli_the_geom_gist

DROP INDEX IF EXISTS public.inli_the_geom_gist;

CREATE INDEX inli_the_geom_gist
    ON public.inli USING gist
    (the_geom);

-- Index: inlity_idx

DROP INDEX IF EXISTS public.inlity_idx;

CREATE INDEX inlity_idx
    ON public.inli USING btree
    (inlity);
