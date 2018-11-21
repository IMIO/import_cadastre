-- Table: public.inpt

DROP TABLE IF EXISTS public.inpt;

DROP SEQUENCE IF EXISTS public.inpt_gid_seq;

CREATE SEQUENCE public.inpt_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.inpt
(
    gid integer NOT NULL DEFAULT nextval('inpt_gid_seq'),
    inptty character varying(2),
    inpttx character varying(50),
    sheet character varying(18),
    the_geom geometry,
    CONSTRAINT inpt_pkey PRIMARY KEY (gid),
    CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'POINT'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);

-- Index: inpt_the_geom_gist

-- DROP INDEX public.inpt_the_geom_gist;

CREATE INDEX inpt_the_geom_gist
    ON public.inpt USING gist
    (the_geom);
