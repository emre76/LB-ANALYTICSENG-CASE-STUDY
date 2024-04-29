{{ config(materialized='incremental')    }}

{%- set source_model = "lb__products__stage"   -%}
{%- set src_pk = "PRODUCTS_HK"          -%}
{%- set src_nk = "id"          -%}
{%- set src_ldts = "LOAD_DATETIME"      -%}
{%- set src_source = "SOURCE"    -%}

{{ automate_dv.hub(src_pk=src_pk, src_nk=src_nk, src_ldts=src_ldts,
                   src_source=src_source, source_model=source_model) }}