DROP TABLE IF EXISTS public.pe;

CREATE TABLE public.pe
(
    pe character varying(424),
    cod character varying(30),
    daa double precision,
    pos smallint,
    adr1 character varying(60),
    adr2 character varying(88),
    lt character varying(4),
    dr character varying(90),
    dr2 character varying(6)
);

DROP INDEX IF EXISTS public.pe_daa_idx;

CREATE INDEX pe_daa_idx
        ON public.pe USING btree
        (daa );
