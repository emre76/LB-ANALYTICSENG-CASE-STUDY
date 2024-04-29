{{ config(materialized='pit_incremental') }}

{%- set yaml_metadata -%}
source_model: h_lb__prices
src_pk: PRICES_HK
as_of_dates_table: as_of_date
satellites: 
  s_lb__prices:
    pk:
      PK: PRICES_HK
    ldts:
      LDTS: LOAD_DATETIME
stage_tables: 
  lb__prices__stage: LOAD_DATETIME
src_ldts: LOAD_DATETIME
{%- endset -%}

{% set metadata_dict = fromyaml(yaml_metadata) %}

{% set source_model = metadata_dict['source_model'] %}
{% set src_pk = metadata_dict['src_pk'] %}
{% set as_of_dates_table = metadata_dict['as_of_dates_table'] %}
{% set satellites = metadata_dict['satellites'] %}
{% set stage_tables_ldts = metadata_dict['stage_tables_ldts'] %}
{% set src_ldts = metadata_dict['src_ldts'] %}

{{ automate_dv.pit(source_model=source_model, src_pk=src_pk,
                   as_of_dates_table=as_of_dates_table,
                   satellites=satellites,
                   stage_tables_ldts=stage_tables_ldts,
                   src_ldts=src_ldts) }}