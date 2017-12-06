-- Table: public.gepn

DROP TABLE IF EXISTS public.gepn;

DROP SEQUENCE IF EXISTS public.gepn_gid_seq;

CREATE SEQUENCE public.gepn_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.gepn
(
    gid integer NOT NULL DEFAULT nextval('gepn_gid_seq'),
    gepnty character varying(2),
    gepnna character varying(50),
    sheet character varying(18),
    the_geom geometry,
    CONSTRAINT gepn_pkey PRIMARY KEY (gid),
    CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    --CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'MULTIPOLYGON'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);

-- Index: gepn_pk_idx

DROP INDEX IF EXISTS public.gepn_pk_idx;

CREATE UNIQUE INDEX gepn_pk_idx
    ON public.gepn USING btree
    (gid);

-- Index: gepn_the_geom_gist

DROP INDEX IF EXISTS public.gepn_the_geom_gist;

CREATE INDEX gepn_the_geom_gist
    ON public.gepn USING gist
    (the_geom);

-- Index: gepnty_idx

DROP INDEX IF EXISTS public.gepnty_idx;

CREATE INDEX gepnty_idx
    ON public.gepn USING btree
    (gepnty);
