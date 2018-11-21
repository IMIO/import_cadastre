DROP TABLE IF EXISTS public.cabu;
DROP INDEX IF EXISTS public.cabu_the_geom_gist;
DROP INDEX IF EXISTS public.cabuty_idx;

DROP SEQUENCE IF EXISTS public.cabu_gid_seq;

CREATE SEQUENCE public.cabu_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.cabu
(
    gid integer NOT NULL DEFAULT nextval('cabu_gid_seq'),
    cabuty character varying(2),
    sheet character varying(18),
    the_geom geometry,
    CONSTRAINT cabu_pkey PRIMARY KEY (gid),
    CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    --CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'POLYGON'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);


CREATE INDEX cabu_the_geom_gist
    ON public.cabu USING gist
    (the_geom);

CREATE INDEX cabuty_idx
    ON public.cabu USING btree
    (cabuty );
