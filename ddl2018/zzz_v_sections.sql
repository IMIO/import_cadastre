-- View: public.v_sections

DROP VIEW IF EXISTS public.v_sections;

CREATE OR REPLACE VIEW public.v_sections AS
 SELECT DISTINCT capa.section,
    capa.section::text AS section_text
   FROM capa;
