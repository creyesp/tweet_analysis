
# Data Pipeline

## AIM roles
CREATE SERVICE ACCOUNT 
Step 1: Filling in desired details
Step 2: Adding „Pub/Sub Editor“ and „BigQuery Data Editor“ roles
Step 3: Downloading JSON key file by choosing CREATE KEY option

## Producer 
Cretea a code to listen tweets, the create a compute engine to run the code
	- write the code (send raw data to clouPubSub)
	- create a compute engine (small-xxx)
	- download credential
	- upload code and credential to compute engine
	- run the code

The code could be a listener or use the api search of twitter.
To enable ssh connection need to upload your public ssh key.


## Pub/sub Topic 
create a topic on PubSub service

## Consumer 
	create a simple funtion to consume messages and send to BQ
		cloudfunction -> Storage/bigquery
	creata  a full data process with apache beam
		dataflow -> Storage/bigquery

## Storage tweets
	BigQuery table
		definir la los campos de la tabla
	Google Storage


# Extra GCP
* DataProc (apache sparck y apache beam)
* DataPrep (preprocesamiento con entorno visual batch y programando)
* DataFlow ()


# References
[Adquiring historical data from twitter](https://medium.com/@poconnell732/acquiring-free-historical-geo-located-data-from-twitter-1f8f2821e9b1)
[copy-data-from-pub-sub-to-bigquery](https://medium.com/@milosevic81/copy-data-from-pub-sub-to-bigquery-496e003228a1)
