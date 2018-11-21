-- Table: public.gept


DROP TABLE IF EXISTS public.gept;
DROP INDEX IF EXISTS public.gept_the_geom_gist;
DROP SEQUENCE IF EXISTS public.gept_gid_seq;

CREATE SEQUENCE public.gept_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.gept
(
    gid integer NOT NULL DEFAULT nextval('gept_gid_seq'::regclass),
    geptty character varying(2),
    geptna character varying(100),
    sheet character varying(18),
    the_geom geometry,
    CONSTRAINT gept_pkey PRIMARY KEY (gid),
    CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'POINT'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);

CREATE INDEX gept_the_geom_gist
    ON public.gept USING gist
    (the_geom);
