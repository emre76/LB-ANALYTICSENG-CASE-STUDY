{{ config(materialized='table') }}

{%- set datepart = "day" -%}
{%- set start_date = "PARSE_DATE('%Y/%m/%d', '2020/09/01')" -%}
{%- set end_date = "PARSE_DATE('%Y/%m/%d', '2021/02/01')" -%}

WITH as_of_date AS (
    {{ dbt_utils.date_spine(datepart=datepart, 
                            start_date=start_date,
                            end_date=end_date) }}
)

SELECT DATE_{{datepart}} as AS_OF_DATE FROM as_of_date
