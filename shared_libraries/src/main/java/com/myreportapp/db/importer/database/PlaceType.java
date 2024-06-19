package com.myreportapp.db.importer.database;

public enum PlaceType {
	CONTINENT(1, "continent"),
    EMPIRE(2, "empire"),
    COUNTRY(3, "country"),
    REGION(4, "region"),
    COUNTY(5, "county"),
    LOCALADMIN(6, "localadmin"),
    BOROUGH(7, "borough"),
    LOCALITY(8, "locality"),
    CAMPUS(9, "campus"),
    NEIGHBOURHOOD(10, "neighbourhood"),
    MACROHOOD(11, "macrohood"),
    MICROHOOD(12, "microhood"),
    POSTALCODE(13, "postalcode");

    private final int id;
    private final String name;

    PlaceType(int id, String name) {
        this.id = id;
        this.name = name;
    }

    public int getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public static PlaceType fromName(String name) {
        for (PlaceType type : PlaceType.values()) {
            if (type.getName().equalsIgnoreCase(name)) {
                return type;
            }
        }
        return null; // or throw an exception if name not found
    }

    public static int getIdFromName(String name) {
        PlaceType type = fromName(name);
        return type != null ? type.getId() : -1;
    }
}