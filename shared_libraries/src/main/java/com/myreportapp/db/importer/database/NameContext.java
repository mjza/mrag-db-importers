package com.myreportapp.db.importer.database;

//convert privateuse in names table of wof to our ids 
public enum NameContext {
	COLLOQUIAL(1, "colloquial"), 
	HISTORICAL(2, "historical"), 
	OFFICIAL(3, "official"), 
	PREFERRED(4, "preferred"),
	PREFERRED_ABBREVIATION(5, "preferred_abbreviation"), 
	UNKNOWN(6, "unknown"), 
	VARIANT(7, "variant");

	private final int id;
	private final String name;

	NameContext(int id, String name) {
		this.id = id;
		this.name = name;
	}

	public int getId() {
		return id;
	}

	public String getName() {
		return name;
	}

	public static int getIdByName(String name) {
		for (NameContext context : NameContext.values()) {
			if (context.getName().equalsIgnoreCase(name)) {
				return context.getId();
			}
		}
		return -1;
	}

	// Example usage
	public static void main(String[] args) {
		int id = NameContext.getIdByName("official");
		System.out.println("ID for 'official': " + id);
	}
}