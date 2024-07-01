### Step 0: Import OSM into Postgre DB
1. You need to go to Documentation within [https://osm2pgsql.org/](https://osm2pgsql.org/) and install it on your machine. I have downloaded a X64 zip file and extracted in `user/AppData/local`.
2. Then you need to download a `.osm.pbf` file from [https://download.geofabrik.de/](https://download.geofabrik.de/).
3. Assuming you have downloaded the data from Geofabrik, the following command will help store the data in a Postgres database. First, create a database. For example, name it `osm`. Then, run the following commands to install extensions on it:

```sql
CREATE DATABASE osm;
CREATE EXTENSION postgis;
CREATE EXTENSION hstore;
```

4. Then, open a terminal in the place where you have downloaded `alberta-latest.osm.pbf` and run the following command:

```bash
osm2pgsql -d osm -U postgres -H localhost -W -C 2000 --create --slim --multi-geometry --latlong --hstore-all --reproject-area --hstore-add-index --extra-attributes --keep-coastlines ./alberta-latest.osm.pbf
```

In windows you need to provide the address to the default.style file using -S option. Therefore, use the following command if we assume you have unzipped the downloaded osm2pgsql in C:\Users\mahdi\AppData\Local\osm2pgsql\default.style.

```bash
osm2pgsql -d osm -U postgres -H localhost -W -S 'C:\Users\mahdi\AppData\Local\osm2pgsql\default.style' -C 2000 --create --slim --multi-geometry --latlong --hstore-all --reproject-area --hstore-add-index --extra-attributes --keep-coastlines ./alberta-latest.osm.pbf
```

Options Breakdown:

- `osm2pgsql`: The executable file to run.
- `-d osm`: The name of the PostgreSQL database.
- `-U postgres`: The PostgreSQL username.
- `-H localhost`: The host (usually localhost for local installations).
- `-W`: Prompt for the PostgreSQL password.
- `-C 2000`: Amount of memory (in MB) to allocate for cache (adjust according to your system).
- `--create`: Create the database schema.
- `--slim`: Use slim mode, necessary for larger imports.
- `--multi-geometry`: Use 3D geometries.
- `--latlong`: Store data in degrees of latitude & longitude (WGS84).
- `--hstore-all`: Add all tags to an additional hstore (key/value) column.
- `--reproject-area`: Compute area column using Web Mercator coordinates.
- `--hstore-add-index`: Add index to hstore (key/value) column.
- `--extra-attributes`: Include attributes (version, timestamp, changeset id, user id, and user name) for each OSM object.
- `--keep-coastlines`: Keep coastline data (default: discard objects tagged natural=coastline).

Mainly you will have these list of tables:

```
osm2pgsql_properties
planet_osm_ways
planet_osm_users
planet_osm_nodes
planet_osm_rels
planet_osm_line
planet_osm_point
planet_osm_polygon
planet_osm_roads
```

And the data of the addresses is stored in the tags column of the `planet_osm_polygon`

For example, for retriving my old address you can run this query:

```sql
SELECT *
FROM planet_osm_polygon pop
WHERE
tags @> '"addr:housenumber"=>"4515"' and
tags @> '"addr:city"=>"Calgary"'
;
```

Then we need to create a mrag table to store converted data:

```sql
-- DROP TABLE public.mrag_ca_addresses;

CREATE TABLE public.mrag_ca_addresses (
	id varchar(32) NOT NULL,
	group_id int4 NULL,
	geo_latitude numeric NULL,
	geo_longitude numeric NULL,
	geo_location public.geometry(point, 4326) NULL,
	street_name varchar(50) NULL,
	street_type varchar(20) NULL,
	street_quad varchar(10) NULL,
	street_full_name varchar(100) NULL,
	street_no varchar(30) NULL,
	house_number int4 NULL,
	house_alpha varchar(30) NULL,
	unit varchar(50) NULL,
	city varchar(255) NULL,
	region varchar(255) NULL,
	postal_code varchar(20) NULL,
	full_address text NULL,
	is_valid bool DEFAULT true NULL,
  boundary public.geometry(geometry, 4326) NULL,
	CONSTRAINT mrag_ca_addresses_pkey PRIMARY KEY (id)
);
CREATE INDEX mrag_ca_addresses_idx_by_full_address ON public.mrag_ca_addresses USING btree (full_address);
CREATE INDEX mrag_ca_addresses_idx_by_geo_location ON public.mrag_ca_addresses USING gist (geo_location);
CREATE INDEX mrag_ca_addresses_idx_by_region ON public.mrag_ca_addresses USING btree (region);
CREATE INDEX mrag_ca_addresses_idx_by_street_full_name ON public.mrag_ca_addresses USING btree (street_full_name);

-- Table Triggers

CREATE OR
REPLACE FUNCTION mrag_function_update_geo_location () RETURNS TRIGGER AS $$
BEGIN
	IF NEW.geo_latitude IS NOT NULL
	AND NEW.geo_longitude IS NOT NULL THEN
		NEW.geo_location = st_setsrid(
			st_makepoint(
				NEW.geo_longitude,
				NEW.geo_latitude
			),
			4326
		);
	ELSE
		NEW.geo_location = NULL;
	END IF;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION mrag_function_update_geo_location () IS 'geo_location is always calculated based on geo_latitude and geo_longitude, 
and any direct attempt to update geo_location is ignored, with the column being recalculated from geo_latitude and geo_longitude instead.';

CREATE TRIGGER mrag_ca_addresses_tr_update_geo_location BEFORE INSERT
OR UPDATE ON
public.mrag_ca_addresses FOR EACH ROW EXECUTE FUNCTION mrag_function_update_geo_location();

--
CREATE OR REPLACE FUNCTION split_street_no()
RETURNS TRIGGER AS $$
DECLARE
  full_street_no text;
  number_part text;
  alpha_part text;
  unit_part text;
  part text;
  parts text[];
BEGIN
  -- Split the street_no into parts based on semicolons
  parts := regexp_split_to_array(NEW.street_no, ';');

  -- Initialize variables
  full_street_no := '';
  number_part := '';
  alpha_part := '';
  unit_part := '';

  -- Iterate through each part to process
  FOREACH part IN ARRAY parts LOOP
    -- Remove leading non-digit characters
    part := regexp_replace(part, '^[^0-9]*', '', 'g');

    -- Extract unit part if present (e.g., 101-375 -> unit is 101)
    IF position('-' in part) > 0 THEN
      unit_part := split_part(part, '-', 1);
      part := split_part(part, '-', 2);
    END IF;

    -- Extract number part until the first non-digit character
    number_part := regexp_replace(part, '^([0-9]+).*', '\1', 'g');

    -- Extract alpha part starting from the first non-digit character
    alpha_part := regexp_replace(part, '^[0-9]+', '', 'g');

    -- Append the parts to full_street_no
    IF full_street_no != '' THEN
      full_street_no := full_street_no || ';';
    END IF;
    full_street_no := full_street_no || number_part || alpha_part;
  END LOOP;

  -- Set the processed full_street_no back to NEW.street_no
  NEW.street_no := full_street_no;

  -- Set unit part
  NEW.unit := unit_part;

  -- Convert number part to integer, handle null case
  IF number_part IS NOT NULL AND number_part != '' THEN
    NEW.house_number := number_part::int;
  ELSE
    NEW.house_number := NULL;
  END IF;

  -- Set alpha part, handle null case
  IF alpha_part IS NOT NULL AND alpha_part != '' THEN
    NEW.house_alpha := alpha_part;
  ELSE
    NEW.house_alpha := NULL;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_split_street_no
BEFORE INSERT OR UPDATE ON mrag_ca_addresses
FOR EACH ROW
EXECUTE FUNCTION split_street_no();

--
CREATE OR REPLACE FUNCTION format_postal_code()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.postal_code IS NOT NULL THEN
    -- Remove any existing spaces
    NEW.postal_code := REPLACE(NEW.postal_code, ' ', '');
    
    -- Format the postal code if it has at least 6 characters
    IF LENGTH(NEW.postal_code) = 6 THEN
      NEW.postal_code := UPPER(SUBSTRING(NEW.postal_code FROM 1 FOR 3)) || ' ' || UPPER(SUBSTRING(NEW.postal_code FROM 4));
    ELSE
      -- Ensure the postal code is in uppercase if it's incomplete
      NEW.postal_code := UPPER(NEW.postal_code);
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_format_postal_code
BEFORE INSERT OR UPDATE ON mrag_ca_addresses
FOR EACH ROW
EXECUTE FUNCTION format_postal_code();
```

### Step 1: Create a Virtual Environment

1.  **Navigate to your project directory**:

```
cd /path/to/your/project
```

2. **Create a virtual environment**:

```
python -m venv venv
```

Use `python3` in commands in MAC.

3.  **Activate the virtual environment**:
    
    -   On Windows:
        
        ```
        venv\Scripts\activate
        ```
        
    -   On macOS/Linux:
        
        ```
        source venv/bin/activate
        ```
        

### Step 2: Create a `requirements.txt` File

Create a `requirements.txt` file in your project directory if you don't have it and add the necessary dependencies:

```
shapely
psycopg2-binary
python-dotenv
```

### Step 3: Install Dependencies

With the virtual environment activated, install the dependencies listed in `requirements.txt`:

```
pip install -r requirements.txt
```

### Step 4: Verify Installation

Verify that the packages are installed correctly by listing installed packages:

```
pip list
```

You should see `shapely`, `psycopg2-binary`, and `python-dotenv` listed among the installed packages.

### Step 5: Running Your Script

Ensure your virtual environment is activated and then run your script:

```
python main.py
```

# Queries

## For making administrative boundaries

Create a table to store boundaries:

```sql
CREATE TABLE mrag_boundary_data (
    name VARCHAR(255),
    place VARCHAR(255),
    center public.geometry(point, 4326),
    bound public.geometry(geometry, 4326)
);
```

And then fill it with: 

```sql
INSERT INTO mrag_boundary_data (name, place, center, bound)
SELECT 
    l.name, p.place, p.way AS center, ST_BuildArea((ST_Union(l.way))) AS bound
FROM 
    planet_osm_line l
JOIN 
    planet_osm_point p ON l.name = p.name
WHERE 
	p.place IN ('city', 'state', 'town', 'village', 'hamlet') 
GROUP BY
    l.name, p.place, p.way
ORDER BY 
    CASE 
        WHEN p.place = 'state' THEN 1
        WHEN p.place = 'city' THEN 2
        WHEN p.place = 'town' THEN 3
        WHEN p.place = 'village' THEN 4
        WHEN p.place = 'hamlet' THEN 5
        ELSE 6
    END;
```