# Download an updated version of the resource files

1. Go to [https://geocode.earth/data/whosonfirst/#CA](https://geocode.earth/data/whosonfirst/#CA) and select a country.
2. Download 2 files from SQLite Databases section:
	2.1. `Administrative Boundaries` file. For example, for Canada: [whosonfirst-data-admin-ca-latest.db.bz2](https://data.geocode.earth/wof/dist/sqlite/whosonfirst-data-admin-ca-latest.db.bz2)
	2.2. `Postal Codes` file. For example, for Canada: 	[whosonfirst-data-postalcode-ca-latest.db.bz2](https://data.geocode.earth/wof/dist/sqlite/whosonfirst-data-postalcode-ca-latest.db.bz2)
3. Extract files in `resources\geocode.earth`.	

# create of `loc` files
1. Copy the `connection.txt` file and rename it to `connection1.loc` and `connection2.loc`
2. Edit the content of these two files
3. The `connection1.loc` belongs to `whosonfirst-data-admin-ca-latest.db`, put its address in `connection1.loc` file.
4. The `connection2.loc` belongs to `whosonfirst-data-postalcode-ca-latest.db`, put its address in `connection2.loc` file.


# Build and Run The Application


## Build the Project:

1. Right-click on your project in the Project Explorer.
2. Select `Run As` > `Maven build...`.
3. In the `Goals` field, type `clean package` (this will clean the target directory and package your application).
4. Click `Run`. This will create an executable JAR in the `target` directory of your project.

## Run the Application:

You can run the application directly from Eclipse or using the command line.

### From command line
1. To run from the command line, navigate to the target directory and use the command: `java -jar com.reportcycle.db.importer.countries-1.0-SNAPSHOT.jar`.

### Inside the IDE
1. Right-click on the project in the Project Explorer.
2. Select `Run As` > `Maven build...`.
3. In the Goals field, enter `compile exec:java -Dexec.mainClass=com.myreportapp.db.importer.CAAddressImporter`.
4. Click Run.