package com.myreportapp.db.importer;

import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.List;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import org.json.JSONArray;
import org.json.JSONObject;
import com.myreportapp.db.importer.config.ColumnMapping;
import com.myreportapp.db.importer.config.TableMapping;
import com.myreportapp.db.importer.database.DatabaseUpdater;
import com.myreportapp.db.importer.trace.MyLogger;

public class CountriesImporter {
	private static MyLogger logger = MyLogger.getInstance(CountriesImporter.class);
	// Main data
	private static final String JSON_MAPPING_FILE = "settings/mapping.json";
	private static final String DB_CONFIG_FILE = "settings/connection.loc";


	// Main method
	public static void main(String[] args) {
		try {
				logger.debug("Application is started.");
				DatabaseUpdater dbu = new DatabaseUpdater(JSON_MAPPING_FILE, DB_CONFIG_FILE);
				Connection conn = dbu.getPostgresConn();
				List<TableMapping> tables = dbu.getConfig().tables;				
				for(TableMapping table : tables) {	
					if (!table.active)
						continue;
					// Construct SQL query using configuration mappings
					StringBuilder rawQuery = new StringBuilder(dbu.buildUpdateQuery(table));
					logger.info("SQL query template made: " + rawQuery.toString());
					// Get source address
					String filePath = table.sourceFileAddress;
					if(filePath.endsWith("csv")) {
						processCSVFile(table, rawQuery, conn, dbu.isStopOnExceptions(), dbu.getDataDirectoryPath());
					} else if(filePath.endsWith("json")) {
						processJSONFile(table, rawQuery, conn, dbu.isStopOnExceptions());
					}
				}
				conn.close();
				logger.debug("Application is stopped.");
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	private static void processCSVFile(TableMapping table, StringBuilder updateQuery, Connection conn, boolean stopOnExceptions, String dataDirectory ) throws Exception {
		String filePath = table.sourceFileAddress;
		logger.debug("Processing information of:" + filePath);		
		// Read CSV file
		FileReader in = new FileReader(filePath);
		Iterable<CSVRecord> records = CSVFormat.DEFAULT.withFirstRecordAsHeader().parse(in);
		logger.debug("CSV file loaded.");
		int totalAffectedRows = 0;
		for (CSVRecord record : records) {
			logger.info("Record: " + record);
			if (!recordIsValid(record)) {
				continue;
			}
			logger.info("Record is valid.");
			String query = updateQuery.toString();			
			PreparedStatement pstmt = conn.prepareStatement(query);
			for (int i = 0; i < table.columns.size(); i++) {
				ColumnMapping columnMapping = table.columns.get(i);
				String csvColumn = columnMapping.source;
				String value = record.get(csvColumn);
				String type = columnMapping.type;
				if("boundary".equals(type)) {
					Path geoJsonPath = Path.of(dataDirectory, value);
					value = loadBoundaryData(geoJsonPath.toString());
				}
				DatabaseUpdater.setPreparedStatementValue(pstmt, i + 1, value, type);
			}
			try {
				// Having this try/catch allows us that if there is a DB exception it does not stop the process
				int affectedRows = pstmt.executeUpdate();
				totalAffectedRows += affectedRows;
				logger.info("Number of affected rows: " + affectedRows);
			} catch (Exception e) {
				e.printStackTrace();
				logger.debug("Record: " + record);
				logger.debug("Error: " + e.getMessage());
				logger.error(e.getMessage(), e);
				if (stopOnExceptions)								
					throw e;
			}
		}
		in.close();
		logger.debug("Total number of affected rows: " + totalAffectedRows);
	}

	private static boolean recordIsValid(CSVRecord record) {
		// Check if the record number is beyond the header row
		if (record.getRecordNumber() < 1) {
			return false;
		}
		return true;
	}
	
	private static String loadBoundaryData(String geoJsonPath) {
		try {
			String geoJsonContent = new String(Files.readAllBytes(Paths.get(geoJsonPath)));
			return geoJsonContent;
		} catch (Exception e) {
			return null;
		}
	}
	
	private static void processJSONFile(TableMapping table, StringBuilder updateQuery, Connection conn, boolean stopOnExceptions ) throws IOException, SQLException {
		String filePath = table.sourceFileAddress;
		logger.debug("Processing information of:" + filePath);		
		// Read JSON file
		String jsonString = new String(Files.readAllBytes(Paths.get(filePath)));
		JSONObject jsonObject = new JSONObject(jsonString);
		JSONArray countriesArray = jsonObject.getJSONObject("countries").getJSONArray("country");
		logger.debug("JSON file loaded.");
		int totalAffectedRows = 0;
		for (int i = 0; i < countriesArray.length(); i++) {
			JSONObject record = countriesArray.getJSONObject(i);
			logger.info("Record: " + record.toString());
			if (!recordIsValid(record)) {
				continue;
			}
			logger.info("Record is valid.");
			String query = updateQuery.toString();			
			PreparedStatement pstmt = conn.prepareStatement(query);
			for (int j = 0; j < table.columns.size(); j++) {
				ColumnMapping columnMapping = table.columns.get(j);
				String jsonIndex = columnMapping.source;
				String value = record.getString(jsonIndex);
				String type = columnMapping.type;				
				DatabaseUpdater.setPreparedStatementValue(pstmt, j + 1, value, type);
			}
			try {
				// Having this try/catch allows us that if there is a DB exception it does not stop the process
				int affectedRows = pstmt.executeUpdate();
				totalAffectedRows += affectedRows;
				logger.info("Number of affected rows: " + affectedRows);
			} catch (Exception e) {
				e.printStackTrace();
				logger.debug("Record: " + record);
				logger.debug("Error: " + e.getMessage());
				logger.error(e.getMessage(), e);
				if (stopOnExceptions)								
					throw e;
			}
		}
		logger.debug("Total number of affected rows: " + totalAffectedRows);
	}
	
	private static boolean recordIsValid(JSONObject record) {
		return true;
	}	
}
