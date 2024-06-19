package com.myreportapp.db.importer.config;

public class ColumnIndexMapping {
	private String columnName;
    public String getColumnName() {
		return columnName;
	}

	private int index;
	public int getIndex() {
		return index;
	}
	
	public ColumnIndexMapping(String columnName, int index) {
        this.columnName = columnName;
        this.index = index;
    }
}
