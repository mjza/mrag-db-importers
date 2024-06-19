package com.myreportapp.db.importer;

import com.myreportapp.db.importer.config.TableMapping;
import com.myreportapp.db.importer.database.DatabaseUpdater;
import com.myreportapp.db.importer.trace.MyLogger;
import java.io.IOException;
import java.sql.*;
import java.util.List;

public class WofImporter {

	private static MyLogger logger = MyLogger.getInstance(WofImporter.class);
	//
	// Main data
	private static final String JSON_MAPPING_FILE = "settings/mapping.json";
	private static final String DB_CONFIG_FILE = "settings/connection.loc";

	//
	private static void processSqliteFile(TableMapping table, Connection sqliteConn, String selectQuery,
			Connection postgresConn, StringBuilder updateQuery, boolean stopOnExceptions)
			throws IOException, SQLException {
		String filePath = table.sourceFileAddress;
		logger.debug("Processing information of:" + filePath);
		// Read sqlite file
		PreparedStatement stmt = sqliteConn.prepareStatement(selectQuery);
		ResultSet rs = stmt.executeQuery();		
		// truncate if read was successful.
		if (table.truncateBeforeInsert) {
			String truncateQuery = "TRUNCATE TABLE " + table.destinationTable;
			Statement truncateStmt = postgresConn.createStatement();
			truncateStmt.execute(truncateQuery);
			logger.info("Truncated table: " + table.destinationTable);
		}
		int row = 0, totalAffectedRows = 0;
		while (rs.next()) {
			row++;
			try (PreparedStatement pstmt = postgresConn.prepareStatement(updateQuery.toString())) {
				DatabaseUpdater.setPreparedStatementValues(pstmt, table.columns, rs);
				int affectedRows = pstmt.executeUpdate();
				totalAffectedRows += affectedRows;
				logger.info("Number of affected rows: " + affectedRows);
			} catch (Exception e) {
				logger.debug("Query: " + updateQuery);
				logger.debug("Row number: " + row);
				logger.error(e.getMessage(), e);
				e.printStackTrace();
				if (stopOnExceptions)
					throw e;
			}
		}
		logger.debug("Total number of affected rows: " + totalAffectedRows);
	}

	//
	public static void main(String[] args) {
		logger.debug("Application is started.");
		try {
			DatabaseUpdater dbu = new DatabaseUpdater(JSON_MAPPING_FILE, DB_CONFIG_FILE);
			Connection postgresConn = dbu.getPostgresConn();
			List<TableMapping> tables = dbu.getConfig().tables;
			for (TableMapping table : tables) {
				if (!table.active)
					continue;
				// Construct SQL query using configuration mappings
				StringBuilder rawQuery = new StringBuilder(dbu.buildUpdateQuery(table));
				logger.debug("SQL update query template made: " + rawQuery.toString());
				// Get source address
				String filePath = table.sourceFileAddress;
				if (filePath.endsWith("db")) {
					dbu.connectToSqlite(filePath);
					Connection sqliteConn = dbu.getSqliteConn();
					logger.debug("Made the Sqlite connection.");
					String selectQuery = dbu.buildSelectQuery(table);
					logger.debug(selectQuery);
					processSqliteFile(table, sqliteConn, selectQuery, postgresConn, rawQuery, dbu.isStopOnExceptions());
					sqliteConn.close();
				}
			}
			postgresConn.close();
			logger.debug("Application is stopped.");
		} catch (Exception e) {
			logger.debug("Error:" + e.getMessage());
			logger.error("Migration failed: ", e);
			e.printStackTrace();
		}
	}

}
