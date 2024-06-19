package com.myreportapp.db.importer.database;

public enum GeometryType {
    POINT(1, "Point"),
    MULTIPOINT(2, "MultiPoint"),
    LINESTRING(3, "LineString"),
    MULTILINESTRING(4, "MultiLineString"),
    POLYGON(5, "Polygon"),
    MULTIPOLYGON(6, "MultiPolygon"),
    GEOMETRYCOLLECTION(7, "GeometryCollection");

    private final int id;
    private final String name;

    GeometryType(int id, String name) {
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
        for (GeometryType type : GeometryType.values()) {
            if (type.getName().equalsIgnoreCase(name)) {
                return type.getId();
            }
        }
        throw new IllegalArgumentException("No constant with name " + name + " found");
    }

    // Example usage
    public static void main(String[] args) {
        int id = GeometryType.getIdByName("Polygon");
        System.out.println("ID for 'Polygon': " + id);
    }
}

