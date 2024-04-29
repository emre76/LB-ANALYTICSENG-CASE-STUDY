{{ config(materialized='view') }}

{%- set yaml_metadata -%}
source_model: 
  src__lichtblick: "lb__products__ext"
derived_columns: 
  SOURCE: "!1"
  LOAD_DATETIME: "PARSE_DATETIME('%Y%m%d%H%M%S',cast(part_datetime as STRING))"
  EFFECTIVE_FROM: "CAST(modificationdate as DATE)"
  START_DATE: "CAST(modificationdate as DATE)"
  END_DATE: "CAST('9999-12-31' as DATE)"
hashed_columns:
  PRODUCTS_HK: "id"
  PRODUCTS_HASHDIFF:
    is_hashdiff: true
    columns:
      - "productcode"
      - "productname"
      - "energy"
      - "consumptiontype"
      - "deleted"
{%- endset -%}

{% set metadata_dict = fromyaml(yaml_metadata) %}

{{ automate_dv.stage(include_source_columns=true,
                     source_model=metadata_dict['source_model'],
                     derived_columns=metadata_dict['derived_columns'],
                     null_columns=none,
                     hashed_columns=metadata_dict['hashed_columns'],
                     ranked_columns=none) }}
