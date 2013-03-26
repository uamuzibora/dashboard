Dashboard
=====

Uamuzi Bora dashboard is a website to show case the uamuzibora data. The application has three parts. 

Part 1(aggregate.py): To aggregate and create a snapshot of the current state of the openmrs database. This aggregate is then stored in a mongodb database. The database will consist of a timeline of snapshots to show the evolution of the database. 

Part 2(dashboard.py,get_data.py): A webserver to serve the aggregated data from the mongodb database. 

Part 3(index.html): The actual website that requestes the data using jquery ajax.


To install program install mongodb and create a database. Create dbConfig.py from the dbConfig.py.default with the configuration for the openmrs database. 

To run start dashboard.py. This will create /tmp/fcgi2.sock which can then be served over a fastCGI server. 