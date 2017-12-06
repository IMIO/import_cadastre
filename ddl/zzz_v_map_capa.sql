-- View: public.v_map_capa

DROP MATERIALIZED VIEW IF EXISTS public.v_map_capa;
DROP INDEX IF EXISTS vmapcapa_the_geom_gist;
DROP INDEX IF EXISTS vmapcapa_codeparcelle_idx;

CREATE MATERIALIZED VIEW public.v_map_capa AS
 SELECT
    ROW_NUMBER() OVER (ORDER BY map.capakey ASC) AS ROW_NUMBER,
    map.capakey,
    map.capakey AS codeparcelle,
    map.urbainkey,
    prc.daa,
    prc.ord,
    map.sl1,
    map.prc,
    map.na1,
    prc.co1,
    map.cod1,
    prc.ri1,
    map.acj,
    map.tv,
    map.prc2,
    capa.capaty,
    capa.shape_area,
    capa.the_geom,
    capa.da,
    capa.section,
    capa.radical,
    capa.exposant,
    capa.bis,
    capa.puissance,
    prc."in",
    prc.ha1,
    prc.rscod,
    array_to_string(ARRAY( SELECT pe.pe
           FROM pe
          WHERE pe.daa = prc.daa
          ORDER BY pe.pos), '; '::text) AS pe,
    array_to_string(ARRAY( SELECT pe.adr1
           FROM pe
          WHERE pe.daa = prc.daa
          ORDER BY pe.pos), '; '::text) AS adr1,
    array_to_string(ARRAY( SELECT pe.adr2
           FROM pe
          WHERE pe.daa = prc.daa
          ORDER BY pe.pos), '; '::text) AS adr2
   FROM map
     JOIN capa ON map.capakey::text = capa.capakey::text
     JOIN prc ON map.capakey = prc.capakey
  ORDER BY map.capakey, map.sl1, (array_to_string(ARRAY( SELECT pe.pe
           FROM pe
          WHERE pe.daa = prc.daa
          ORDER BY pe.pos), '; '::text));

CREATE INDEX vmapcapa_the_geom_gist ON public.v_map_capa USING gist (the_geom);
CREATE INDEX vmapcapa_codeparcelle_idx
    ON public.v_map_capa USING btree
    (codeparcelle );
