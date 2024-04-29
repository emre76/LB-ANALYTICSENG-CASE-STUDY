# NOTES

This ELT-Pipeline works on GCP.  
As packaging tool, Poetry is used.


This Lichtblick case-study implementation has 2 parts:

### INGESTION
This python program is a in Click implemented CLI-Application, that takes  a monthly table batch and saves it in the GCS in a partitioned way. The VSCode Debugger calls can be seen under ".vscode" folder.

### TRANSFORMATIONS

This part links to the data in storage over bigquery external table and runs the transformations via DBT. The Data Modeling follows the Data Vault Methodology over the AutomateDV package.

## RESULTS
There was a bug for DBT Pit macro, so unfortunately, The results couldnt be presented, because of the lack of time too. There were no time left to write some tests as well. The whole work took 7-8 hours in its Status.

