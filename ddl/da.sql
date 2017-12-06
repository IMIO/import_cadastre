DROP TABLE IF EXISTS public.da;

CREATE TABLE public.da
(
    da bigint NOT NULL,
    dan1 character varying(64),
    lt character varying(2),
    admnr character varying(10),
    da1 character varying(4),
    adm1 character varying(50),
    mut character varying(4),
    dan2 character varying(64),
    adm2 character varying(50),
    divname character varying(50),
    CONSTRAINT da_pk PRIMARY KEY (da)
);
