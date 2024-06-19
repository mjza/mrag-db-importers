package com.myreportapp.db.importer.database;

import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.Date;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.sql.Types;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.stream.Collectors;
import java.util.concurrent.atomic.AtomicInteger;
import org.json.JSONObject;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Polygon;
import org.locationtech.jts.io.ParseException;
import org.locationtech.jts.io.geojson.GeoJsonReader;
import org.postgresql.util.PGobject;
import com.myreportapp.db.importer.config.ConfigReader;
import com.myreportapp.db.importer.config.TableMapping;
import com.myreportapp.db.importer.trace.MyLogger;
import com.myreportapp.db.importer.config.ColumnIndexMapping;
import com.myreportapp.db.importer.config.ColumnMapping;
import com.myreportapp.db.importer.config.Config;

public class DatabaseUpdater {
	private static MyLogger logger = MyLogger.getInstance(DatabaseUpdater.class);
	List<ColumnIndexMapping> columnIndexMappings = new ArrayList<ColumnIndexMapping>();
	private Connection sqliteConn;
	private Connection postgresConn;
	private Config config;
	private boolean stopOnExceptions;
	private String dataDirectoryPath;

	public DatabaseUpdater(String jsonMappingFilePath, String dbConfigFilePath) throws SQLException {
		ConfigReader configReader = ConfigReader.getInstance(jsonMappingFilePath, dbConfigFilePath);
		logger.info("configuration files was fetched.");
		config = configReader.getConfig();
		Properties dbProps = configReader.getProperties();
		postgresConn = DriverManager.getConnection(dbProps.getProperty("url"), dbProps.getProperty("user"),
				dbProps.getProperty("password"));
		stopOnExceptions = "1".equals(dbProps.getProperty("stopOnExceptions"));
		dataDirectoryPath = dbProps.getProperty("dataDirectoryPath");
		logger.info("Connected to destination database.");
	}

	public boolean isStopOnExceptions() {
		return stopOnExceptions;
	}

	public Config getConfig() {
		return config;
	}

	public Connection getSqliteConn() {
		return sqliteConn;
	}

	public Connection getPostgresConn() {
		return postgresConn;
	}

	public void connectToSqlite(String path) throws SQLException {
		sqliteConn = DriverManager.getConnection("jdbc:sqlite:" + path);
	}

	public String getDataDirectoryPath() {
		return dataDirectoryPath;
	}

	public String buildSelectQuery(TableMapping table) {
		String sourceTable = table.sourceTable;
		List<ColumnMapping> columnMappings = table.columns;
		String selectWhereCondition = table.selectWhereCondition;
		String selectOrderBy = table.selectOrderBy;
		String selectGroupBy = table.selectGroupBy;

		StringBuilder query = new StringBuilder("SELECT "); // Do not use DISTINCT as we do not project all columns
		boolean first = true;
		for (ColumnMapping col : columnMappings) {
			if (!first) {
				query.append(", ");
			}
			query.append(col.source);
			first = false;
		}
		query.append(" FROM ").append(sourceTable);
		if (selectWhereCondition != null && selectWhereCondition.trim().length() > 0) {
			query.append(" WHERE ").append(selectWhereCondition);
		}
		if (selectGroupBy != null && selectGroupBy.trim().length() > 0) {
			query.append(" GROUP BY ").append(selectGroupBy);
		}
		if (selectOrderBy != null && selectOrderBy.trim().length() > 0) {
			query.append(" ORDER BY ").append(selectOrderBy);
		}
		return query.toString();
	}

	public String buildUpdateQuery(TableMapping table) {
		if (table.useUpsert)
			return buildUpsertQuery(table);
		// otherwise create pure update query
		String destination = table.destinationTable;
		List<ColumnMapping> columnMappings = table.columns;
		String uniqueIndex = table.uniqueIndex; // assuming this is the column used in the WHERE clause

		// Counter for placeholder index
		AtomicInteger placeholderIndex = new AtomicInteger(1);
		columnIndexMappings.clear(); // Clear previous mappings

		// Creating the SET part of the update statement
		String setClause = columnMappings.stream().filter(c -> !c.destination.equals(uniqueIndex)).map(c -> {
			columnIndexMappings.add(new ColumnIndexMapping(c.destination, placeholderIndex.getAndIncrement()));
			return c.destination + " = " + (c.type.equals("geometry") ? "ST_SetSRID(ST_GeomFromText(?), 4326)" : "?");
		}).collect(Collectors.joining(", "));

		// Add unique index at the end
		columnIndexMappings.add(new ColumnIndexMapping(uniqueIndex, placeholderIndex.get()));

		// Constructing the full UPDATE query
		String query = "UPDATE " + destination + " SET " + setClause + " WHERE " + uniqueIndex + " = ?";

		return query;
	}

	public String buildUpsertQuery(TableMapping table) {
		String destination = table.destinationTable;
		List<ColumnMapping> columnMappings = table.columns;
		String uniqueConstraintColumn = table.uniqueIndex; // assuming this is the column used in the WHERE clause

		// Creating the INSERT part of the statement
		String columnNames = columnMappings.stream().map(c -> c.destination).collect(Collectors.joining(", "));

		String valuePlaceholders = columnMappings.stream()
				.map(c -> (c.type.equals("geometry") ? "ST_SetSRID(ST_GeomFromText(?), 4326)" : "?"))
				.collect(Collectors.joining(", "));

		// Creating the UPDATE part of the statement
		String setClause = columnMappings.stream().filter(c -> !c.destination.equals(uniqueConstraintColumn))
				.map(c -> c.destination + " = EXCLUDED." + c.destination).collect(Collectors.joining(", "));
		StringBuilder query = new StringBuilder();
		// Constructing the full UPSERT query
		query.append("INSERT INTO ").append(destination).append(" (").append(columnNames).append(") VALUES (")
				.append(valuePlaceholders).append(")");
		if (uniqueConstraintColumn != null && uniqueConstraintColumn.trim().length() > 0) {
			query.append(" ON CONFLICT (").append(uniqueConstraintColumn).append(") DO UPDATE SET ").append(setClause);
		}

		return query.toString();
	}

	public int getIndexByColumnName(String columnName) {
		for (ColumnIndexMapping mapping : columnIndexMappings) {
			if (mapping.getColumnName().equals(columnName)) {
				return mapping.getIndex();
			}
		}
		return -1;
	}

	public static void setPreparedStatementValue(PreparedStatement pstmt, int index, String value, String type)
			throws SQLException {
		if (value == null || value.isEmpty()) {
			pstmt.setObject(index, null);
			return;
		}
		try {
			switch (type.toLowerCase()) {
			case "integer":				
				pstmt.setInt(index, Integer.parseInt(value));
				break;
			case "fixed_value":
			case "string":
				pstmt.setString(index, value);
				break;
			case "number":
				pstmt.setBigDecimal(index, new BigDecimal(value));
				break;
			case "double":
				pstmt.setDouble(index, Double.parseDouble(value));
				break;
			case "float":
				pstmt.setFloat(index, Float.parseFloat(value));
				break;
			case "boolean":
				pstmt.setBoolean(index, Boolean.parseBoolean(value));
				break;
			case "long":
				pstmt.setLong(index, Long.parseLong(value));
				break;
			case "short":
				pstmt.setShort(index, Short.parseShort(value));
				break;
			case "byte":
				pstmt.setByte(index, Byte.parseByte(value));
				break;
			case "hause_number":
				pstmt.setInt(index, Integer.parseInt(extractNumber(value)));
				break;
			case "hause_alpha":
				pstmt.setString(index, extractAlpha(value));
				break;
			case "unix_timestamp":
				// Convert Unix timestamp (seconds since epoch) to Java Timestamp
				long unixTime = Long.parseLong(value);
				// Multiply by 1000 to convert to milliseconds
				Timestamp utimestamp = new Timestamp(unixTime * 1000);
				pstmt.setTimestamp(index, utimestamp);
				break;
			case "fixed_timestamp":	
			case "timestamp":
				// Assumes format: yyyy-[m]m-[d]d hh:mm:ss[.f...]
				Timestamp timestamp = Timestamp.valueOf(value);
				pstmt.setTimestamp(index, timestamp);
				break;
			case "timestamptz": // timestamp with time zone
				// Assumes format: yyyy-[m]m-[d]d hh:mm:ss[.f...] with
				Timestamp timestampTz = Timestamp.valueOf(value);
				// time zone
				pstmt.setTimestamp(index, timestampTz);
				break;
			case "date":
				// Assumes format: yyyy-[m]m-[d]d
				Date sqlDate = Date.valueOf(value);
				pstmt.setDate(index, sqlDate);
				break;
			case "tilda-date":
				pstmt.setDate(index, parseCessationDate(value));
				break;
			case "boundary":
				PGobject boundary = extractBoundaryData(value);
				pstmt.setObject(index, boundary);
				break;
			case "geometry_type_id":
				Geometry geometry = extractGeometry(value);
				pstmt.setInt(index, GeometryType.getIdByName(geometry.getGeometryType()));
				break;
			case "bounding_box":
				pstmt.setObject(index, convertBBoxToPolygon(value));
				break;
			case "min_longitude":
			case "min_latitude":
			case "max_longitude":
			case "max_latitude":
				BigDecimal geoVal = extractFromBBox(value, type.toLowerCase());
				pstmt.setBigDecimal(index, geoVal);
				break;
			default:
				pstmt.setObject(index, value);
				break;
			}
		} catch (Exception e) {
			pstmt.setNull(index, Types.OTHER);
		}
	}

	public static void setPreparedStatementValues(PreparedStatement pstmt, List<ColumnMapping> columns, ResultSet rs)
			throws SQLException {
		int index = 1;
		for (ColumnMapping column : columns) {
			String type = column.type;
			String source = column.source;
			try {
				switch (type) {
				case "integer":
					if (source.contains("placetype")) {
						int placeTypeId = PlaceType.getIdFromName(rs.getString(source));
						pstmt.setInt(index, placeTypeId);
						break;
					} else if (source.contains("privateuse")) {
						int contextId = NameContext.getIdByName(rs.getString(source));
						pstmt.setInt(index, contextId);
						break;
					}
					pstmt.setInt(index, rs.getInt(source));
					break;
				case "fixed_value":
					pstmt.setString(index, source);
					break;
				case "string":
					pstmt.setString(index, rs.getString(source));
					break;
				case "number":
					pstmt.setBigDecimal(index, rs.getBigDecimal(source));
					break;
				case "double":
					pstmt.setDouble(index, rs.getDouble(source));
					break;
				case "float":
					pstmt.setFloat(index, rs.getFloat(source));
					break;
				case "boolean":
					pstmt.setBoolean(index, rs.getBoolean(source));
					break;
				case "long":
					pstmt.setLong(index, rs.getLong(source));
					break;
				case "short":
					pstmt.setShort(index, rs.getShort(source));
					break;
				case "byte":
					pstmt.setByte(index, rs.getByte(source));
					break;
				case "unix_timestamp":
					// Convert Unix timestamp (seconds since epoch) to Java Timestamp
					long unixTime = rs.getLong(source);
					// Multiply by 1000 to convert to milliseconds
					Timestamp utimestamp = new Timestamp(unixTime * 1000); 
					pstmt.setTimestamp(index, utimestamp);
					break;
				case "timestamp":
					// Assumes format: yyyy-[m]m-[d]d hh:mm:ss[.f...]
					Timestamp timestamp = Timestamp.valueOf(rs.getString(source)); 
					pstmt.setTimestamp(index, timestamp);
					break;
				case "timestamptz": // timestamp with time zone
					// Assumes format: yyyy-[m]m-[d]d hh:mm:ss[.f...] with
					Timestamp timestampTz = Timestamp.valueOf(rs.getString(source)); 
					// time zone
					pstmt.setTimestamp(index, timestampTz);
					break;
				case "date":
					// Assumes format: yyyy-[m]m-[d]d
					Date sqlDate = Date.valueOf(rs.getString(source)); 
					pstmt.setDate(index, sqlDate);
					break;
				case "tilda-date":
					pstmt.setDate(index, parseCessationDate(rs.getString(source)));
					break;	
				case "boundary":
					PGobject boundary = extractBoundaryData(rs.getString(source));
					pstmt.setObject(index, boundary);
					break;
				case "geometry_type_id":
					Geometry geometry = extractGeometry(rs.getString(source));
					pstmt.setInt(index, GeometryType.getIdByName(geometry.getGeometryType()));
					break;	
				case "bounding_box":
					pstmt.setObject(index, convertBBoxToPolygon(rs.getString(source)));
					break;
				case "min_longitude":
				case "min_latitude":
				case "max_longitude":
				case "max_latitude":
					BigDecimal geoVal = extractFromBBox(rs.getString(source), type.toLowerCase());
					pstmt.setBigDecimal(index, geoVal);
					break;	
				default:
					pstmt.setObject(index, rs.getObject(source));
					break;
				}// end of switch
			} catch (Exception e) {
				pstmt.setNull(index, Types.OTHER);
			}
			index++;
		} // end of for
	}

	// possible values for cessation dates
	// uuuu, 1992-03~, 1991-09~, 1945-11-29, 1991-06~, 2006, ..
	private static Date parseCessationDate(String dateStr) {
		if (dateStr == null || dateStr.isEmpty() || dateStr.equals("uuuu") || dateStr.equals("..")) {
			return null;
		}

		// Replace all '~' with '-01'
		// each ~ is a behaved as first day or first month!
		dateStr = standardizeDate(dateStr.replace("~", "-01"));

		try {
			return Date.valueOf(dateStr); // Convert to SQL date
		} catch (IllegalArgumentException e) {
			return null; // Return null if the date is invalid
		}
	}

	// checks and makes the date exactly 10 digits
	public static String standardizeDate(String dateStr) {

		String[] parts = dateStr.split("-");

		// Return the original string if it already has a day component
		if (parts.length == 3 && dateStr.length() == 10) {
			return dateStr;
		}

		String year = parts[0];
		//
		String month = parts.length > 1 ? parts[1] : "01"; // Default to January if month is missing
		// Format the month to ensure it is two digits
		if (month.length() == 1) {
			month = "0" + month;
		}
		//
		String day = parts.length > 2 ? parts[2] : "01"; // Default to first day if day is missing
		// Format the day to ensure it is two digits
		if (day.length() == 1) {
			day = "0" + day;
		}
		//
		return year + "-" + month + "-" + day;
	}

	// Extracts the numeric part of a string
	public static String extractNumber(String input) {
		return input.replaceAll("[^\\d]", "");
	}

	// Extracts the alphabetic part of a string
	public static String extractAlpha(String input) {
		return input.replaceAll("[^A-Za-z]", "");
	}

	private static PGobject extractBoundaryData(String geoJsonContent) throws ParseException, SQLException {
		Geometry boundaryData = extractGeometry(geoJsonContent);
		PGobject pgObject = new PGobject();
		pgObject.setType("geometry");
		pgObject.setValue(boundaryData.toText());
		return pgObject;
	}

	private static Geometry extractGeometry(String geoJsonContent) throws ParseException {
		JSONObject geoJson = new JSONObject(geoJsonContent);
		GeoJsonReader reader = new GeoJsonReader();
		// The geometry is stored in the "geometry" field of the GeoJSON
		JSONObject geometryJson = geoJson.getJSONObject("geometry");
		Geometry geometry = reader.read(geometryJson.toString());
		return geometry;
	}

	private static PGobject convertBBoxToPolygon(String bboxStr) throws SQLException {

		String[] parts = bboxStr.split(",");
		if (parts.length < 4)
			return null;
		double minLon = Double.parseDouble(parts[0]);
		double minLat = Double.parseDouble(parts[1]);
		double maxLon = Double.parseDouble(parts[2]);
		double maxLat = Double.parseDouble(parts[3]);

		GeometryFactory geometryFactory = new GeometryFactory();

		// Create coordinates for the polygon
		Coordinate[] coordinates = new Coordinate[] { new Coordinate(minLon, minLat), new Coordinate(minLon, maxLat),
				new Coordinate(maxLon, maxLat), new Coordinate(maxLon, minLat), new Coordinate(minLon, minLat) };

		Polygon polygon = geometryFactory.createPolygon(coordinates);

		PGobject pgPolygon = new PGobject();
		pgPolygon.setType("geometry");
		pgPolygon.setValue(polygon.toString());

		return pgPolygon;
	}

	private static BigDecimal extractFromBBox(String bboxStr, String index) {
		String[] parts = bboxStr.split(",");
		if (parts.length < 4)
			return null;
		double minLon = Double.parseDouble(parts[0]);
		double minLat = Double.parseDouble(parts[1]);
		double maxLon = Double.parseDouble(parts[2]);
		double maxLat = Double.parseDouble(parts[3]);

		switch (index) {
		case "min_longitude":
			return BigDecimal.valueOf(minLon);
		case "min_latitude":
			return BigDecimal.valueOf(minLat);
		case "max_longitude":
			return BigDecimal.valueOf(maxLon);
		case "max_latitude":
			return BigDecimal.valueOf(maxLat);
		default:
			return null;
		}
	}

}
