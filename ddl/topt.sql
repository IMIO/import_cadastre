-- Table: public.topt

DROP TABLE IF EXISTS public.topt;

DROP SEQUENCE IF EXISTS public.topt_gid_seq;

CREATE SEQUENCE public.topt_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.topt
(
    gid integer NOT NULL DEFAULT nextval('topt_gid_seq'),
    toptty character varying(2),
    toptan double precision,
    topttx character varying(255),
    sheet character varying(18),
    the_geom geometry,
    CONSTRAINT topt_pkey PRIMARY KEY (gid),
    CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'POINT'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);

-- Index: topt_pk_idx

DROP INDEX IF EXISTS public.topt_pk_idx;

CREATE UNIQUE INDEX topt_pk_idx
    ON public.topt USING btree
    (gid);

-- Index: topt_the_geom_gist

DROP INDEX IF EXISTS public.topt_the_geom_gist;

CREATE INDEX topt_the_geom_gist
    ON public.topt USING gist
    (the_geom);

-- Index: toptty_idx

DROP INDEX IF EXISTS public.toptty_idx;

CREATE INDEX toptty_idx
    ON public.topt USING btree
    (toptty);
