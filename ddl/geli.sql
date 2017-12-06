
DROP TABLE IF EXISTS public.geli;

DROP SEQUENCE IF EXISTS public.geli_gid_seq;

CREATE SEQUENCE public.geli_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.geli
(
    gid integer NOT NULL DEFAULT nextval('geli_gid_seq'),
    gelity character varying(2),
    sheet character varying(18),
    the_geom geometry,
    CONSTRAINT geli_pkey PRIMARY KEY (gid),
    CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    --CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'MULTILINESTRING'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);

-- Index: geli_pk_idx

DROP INDEX IF EXISTS public.geli_pk_idx;

CREATE UNIQUE INDEX geli_pk_idx
    ON public.geli USING btree
    (gid);

-- Index: geli_the_geom_gist

DROP INDEX IF EXISTS public.geli_the_geom_gist;

CREATE INDEX geli_the_geom_gist
    ON public.geli USING gist
    (the_geom);

-- Index: gelity_idx

DROP INDEX IF EXISTS  public.gelity_idx;

CREATE INDEX gelity_idx
    ON public.geli USING btree
    (gelity);
