DROP TABLE IF EXISTS public.rebu;
DROP INDEX IF EXISTS public.rebu_the_geom_gist;
DROP INDEX IF EXISTS public.rebuty_idx;

DROP SEQUENCE IF EXISTS public.rebu_gid_seq;

CREATE SEQUENCE public.rebu_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.rebu
(
    gid integer NOT NULL DEFAULT nextval('rebu_gid_seq'),
    id_orig character varying(50),
    "type" character varying(10),
    the_geom geometry,
    CONSTRAINT rebu_pkey PRIMARY KEY (gid),
    CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    --CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'POLYGON'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);


CREATE INDEX rebu_the_geom_gist
    ON public.rebu USING gist
    (the_geom);

CREATE INDEX rebuty_idx
    ON public.rebu USING btree
    ("type" );
