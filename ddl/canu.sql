
DROP TABLE IF EXISTS public.canu;
DROP SEQUENCE IF EXISTS public.canu_gid_seq;
DROP INDEX IF EXISTS public.canu_the_geom_gist;

CREATE SEQUENCE public.canu_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.canu
(
    gid integer NOT NULL DEFAULT nextval('canu_gid_seq'),
    canuan double precision,
    canutx character varying(11),
    sheet character varying(18),
    the_geom geometry,
    numpolice character varying(15),
    CONSTRAINT canu_pkey PRIMARY KEY (gid),
    --CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'POINT'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);

CREATE INDEX canu_the_geom_gist
    ON public.canu USING gist
    (the_geom);
