
DROP INDEX IF EXISTS public.capa_the_geom_gist;
DROP INDEX IF EXISTS public.capaty_idx;
DROP TABLE IF EXISTS public.capa CASCADE;
DROP SEQUENCE IF EXISTS public.capa_gid_seq;

CREATE SEQUENCE public.capa_gid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

CREATE TABLE public.capa
(
    gid integer NOT NULL DEFAULT nextval('capa_gid_seq'),
    capakey character varying(17),
    casekey character varying(6),
    the_geom geometry,
    CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
    --CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'MULTIPOLYGON'::text OR the_geom IS NULL),
    CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 31370)
);

ALTER TABLE capa ADD PRIMARY KEY(gid);

CREATE INDEX capa_the_geom_gist
    ON public.capa USING gist
    (the_geom);

CREATE INDEX capakey_idx
    ON public.capa USING btree
    (capakey);
