# 1. Set the connection settings

1. Copy and paste the file `connection.txt` and rename it to `connection.loc`.
2. Edit the content of the loc file based on your postgres database. 

# 2. Download an update the resource files

## 2.1. Main data
1. The data has been downloaded from [geocode.earth](https://geocode.earth/data/boundary/country/).
2. Put the tar file in the `resources\geocode.earth\whosonfirst-data-country-latest` and then unzip it there. It must generate 2 folders `data` and `meta`.

## 2.2. Additional data
1. The `capital_currency_continent.json` JSON file from [this repository](https://gist.github.com/tiagodealmeida/0b97ccf117252d742dddf098bc6cc58a)
2. CSV file for calling codes and iso codes from [here](https://github.com/datasets/country-codes/blob/master/data/country-codes.csv).

You mainly need to clean update these 2 files by hand before using them. 

# 3. Build and Run The Application

## 3.1. Build the Project:

1. Right-click on your project in the Project Explorer.
2. Select `Run As` > `Maven build...`.
3. In the `Goals` field, type `clean package` (this will clean the target directory and package your application).
4. Click `Run`. This will create an executable JAR in the `target` directory of your project.

## 3.2. Run the Application:

You can run the application directly from Eclipse or using the command line. 
*But first you need to make sure the `shared_libraries` has been cleaned and installed.*

### 3.2.1. Install shared libraries
1. Right click on `shared_libraries` and select `maven clean` from Run menu.
2. Do the same but select `maven install`.
3. You need these steps with any changes on `shared_project`.

### 3.2.2. From command line
1. To run from the command line, navigate to the target directory and use the command: `java -jar com.myreportapp.db.importer.CountriesImporter-0.0.1-SNAPSHOT.jar`.

### 3.2.3. Inside the IDE
1. Right-click on the project in the Project Explorer.
2. Select `Run As` > `Maven build...`.
3. In the Goals field, enter `compile exec:java -Dexec.mainClass=com.myreportapp.db.importer.CountriesImporter`.
4. Click Run.