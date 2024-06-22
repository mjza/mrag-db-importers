# Download an updated version of the resource files

1. Go to [https://www.statcan.gc.ca/en/lode/databases/oda](https://www.statcan.gc.ca/en/lode/databases/oda) and download addresses for Canada.
2. Extract files in `resources\`.	

# create of `loc` files
1. Copy the `connection.txt` file and rename it to `connection.loc`.
2. Edit the content of the new file.


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