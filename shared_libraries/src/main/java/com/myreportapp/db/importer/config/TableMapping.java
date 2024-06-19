package com.myreportapp.db.importer.config;

import java.util.List;

public class TableMapping {
	public boolean active;
    public String sourceFileAddress;
    public String sourceTable;
    public String selectWhereCondition;
	public String selectOrderBy;
	public String selectGroupBy;
    public String destinationTable;
    public boolean useUpsert;
    public String uniqueIndex;
    public boolean truncateBeforeInsert;
    public List<ColumnMapping> columns;
}
