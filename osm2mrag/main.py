import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from shapely.wkt import loads as load_wkt
from shapely.geometry import Polygon
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Connect to the PostgreSQL database
def connect_db():
    # Connect to the PostgreSQL database
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Extracted list from https://www.gimme-shelter.com/steet-types-designations-abbreviations-50006/
# Also provided a pdf in the docs forlder for reference. 
REPLACEMENTS = {
    r"\sAbbey\s": r" Abbey ",
    r"\sAC\s": r" Acres ",
    r"\sAcres\s": r" Acres ",
    r"\sAL\s": r" Alley ",
    r"\sALY\s": r" Alley ",
    r"\sAlley\s": r" Alley ",
    r"\sAllée\s": r" Allée ",
    r"\sANX\s": r" Annex ",
    r"\sAnnex\s": r" Annex ",
    r"\sAnex\s": r" Annex ",
    r"\sARC\s": r" Arcade ",
    r"\sArcade\s": r" Arcade ",
    r"\sAUT\s": r" Aut ",
    r"\sAutoroute\s": r" Aut ",
    r"\sAV\s": r" Ave ",
    r"\sAvenue": r" Ave ",
    r"\sBA\s": r" Bay ",
    r"\sBay\s": r" Bay ",
    r"\sBYU\s": r" Bayou ",
    r"\sBayou\s": r" Bayou ",
    r"\sBE\s": r" Beach ",
    r"\sBN\s": r" Bend ",
    r"\sBLF\s": r" Bluff ",
    r"\sBluff\s": r" Bluff ",
    r"\sBLFS\s": r" Bluffs ",
    r"\sBluffs\s": r" Bluffs ",
    r"\sBox\s": r" Box ",
    r"\sBTM\s": r" Bottom ",
    r"\sBottom\s": r" Bottom ",
    r"\sBV\s": r" Blvd ",
    r"\sBoulevard\s": r" Blvd ",
    r"\sBOUL\s": r" Blvd ",
    r"\sBLVD\s": r" Blvd ",
    r"\sBR\s": r" Branch ",
    r"\sBranch\s": r" Branch ",
    r"\sBRG\s": r" Bridge ",
    r"\sBridge\s": r" Bridge ",
    r"\sBYP\s": r" Bypass ",
    r"\sBy-pass\s": r" Bypass ",
    r"\sBypass\s": r" Bypass ",
    r"\sByway\s": r" Byway ",
    r"\sCP\s": r" Camp ",
    r"\sCamp\s": r" Camp ",
    r"\sCampus\s": r" Campus ",
    r"\sCYN\s": r" Canyon ",
    r"\sCanyon\s": r" Canyon ",
    r"\sCPE\s": r" Cape ",
    r"\sCA\s": r" Cape ",
    r"\sCape\s": r" Cape ",
    r"\sCarré\s": r" Car ",
    r"\sCarrefour\s": r" Carref ",
    r"\sCS\s": r" Castle ",
    r"\sCastle\s": r" Castle ",
    r"\sCSWY\s": r" Causeway ",
    r"\sCauseway\s": r" Causeway ",
    r"\sCE\s": r" Ctr ",
    r"\sCentre\s": r" Ctr ",
    r"\sCentres\s": r" Ctr ",
    r"\sCtr\s": r" Ctr ",
    r"\sCTRS\s": r" Ctr ",  
    r"\sCercle\s": r" Cercle ", 
    r"\sChare\s": r" Chare ",
    r"\sChase\s": r" Chase ",
    r"\sChemin\s": r" Ch ",
    # continue
    r"\sCI\s": r" Cir ",
    r"\sCircle\s": r" Cir ",
    r"\sCircuit\s": r" Circt ",
    r"\sCL\s": r" Close ",
    r"\sCM\s": r" Common ",
    r"\sConcession\s": r" Conc ",
    r"\sCorners\s": r" Crnrs ",
    r"\sCO\s": r" Crt ",
    r"\sCourt\s": r" Crt ",
    r"\sCR\s": r" Cres ",
    r"\sCrescent\s": r" Cres ",
    r"\sCV\s": r" Cove ",
    r"\sCrossing\s": r" Cross ",
    r"\sCul-de-sac\s": r" Cds ",
    r"\sDI\s": r" Divers ",
    r"\sDiversion\s": r" Divers ",
    r"\sDO\s": r" Downs ",
    r"\sDR\s": r" Dr ",
    r"\sDrive\s": r" Dr ",
    r"\sEN\s": r" End ",
    r"\sEsplanade\s": r" Espl ",
    r"\sES\s": r" Estate ",
    r"\sExpressway\s": r" Expy ",
    r"\sExtension\s": r" Exten ",
    r"\sFR\s": r" Fwy ",
    r"\sFreeway\s": r" Fwy ",
    r"\sGA\s": r" Gate ",
    r"\sGT\s": r" Gate ",
    r"\sGD\s": r" Gdns ",
    r"\sGardens\s": r" Gdns ",
    r"\sGL\s": r" Glen ",
    r"\sGR\s": r" Green ",
    r"\sGrounds\s": r" Grnds ",
    r"\sGV\s": r" Grove ",
    r"\sHB\s": r" Harbr ",
    r"\sHarbour\s": r" Harbr ",
    r"\sHE\s": r" Heath ",
    r"\sHI\s": r" Hwy ",
    r"\sHighway\s": r" Hwy ",
    r"\sHL\s": r" Hill ",
    r"\sHO\s": r" Hollow ",
    r"\sHT\s": r" Hts ",
    r"\sHeights\s": r" Hts ",
    r"\sHighlands\s": r" Hghlds ",
    r"\sIN\s": r" Inlet ",
    r"\sIS\s": r" Island ",
    r"\sKN\s": r" Knoll ",
    r"\sKY\s": r" Key ",
    r"\sLD\s": r" Landng ",
    r"\sLI\s": r" Link ",
    r"\sLN\s": r" Lane ",
    r"\sLimits\s": r" Lmts ",
    r"\sLookout\s": r" Lkout ",
    r"\sLO\s": r" Loop ",        
    r"\sMA\s": r" Mall ",
    r"\sMD\s": r" Meadow ",
    r"\sME\s": r" Mews ",
    r"\sMR\s": r" Manor ",
    r"\sMT\s": r" Mount ",
    r"\sMountain\s": r" Mtn ",
    r"\sMZ\s": r" Maze ",
    r"\sOrchard\s": r" Orch ",
    r"\sPA\s": r" Pk ",
    r"\sPark\s": r" Pk ",
    r"\sPH\s": r" Path ",
    r"\sPK\s": r" Pky ",
    r"\sPL\s": r" Pl ",
    r"\sPlace\s": r" Pl ",
    r"\sPlateau\s": r" Plat ",
    r"\sPM\s": r" Prom ",
    r"\sPromenade\s": r" Prom ",
    r"\sPR\s": r" Parade ",
    r"\sPS\s": r" Pass ",
    r"\sPassage\s": r" Pass ",
    r"\sPoint\s": r" Pt ",
    r"\sPathway\s": r" Ptway ",
    r"\sPZ\s": r" Plaza ",
    r"\sPrivate\s": r" Pvt ",        
    r"\sQY\s": r" Quay ",
    r"\sRD\s": r" Rd ",
    r"\sRoad\s": r" Rd ",
    r"\sRG\s": r" Ridge ",
    r"\sRange\s": r" Rg ",
    r"\sRI\s": r" Rise ",
    r"\sRoute\s": r" Rte ",
    r"\sRO\s": r" Row ",
    r"\sRU\s": r" Run ",
    r"\sSquare\s": r" Sq ",
    r"\sST\s": r" St ",
    r"\sStreet\s": r" St ",
    r"\sSubdivision\s": r" Subdiv ",
    r"\sTC\s": r" Terr ",
    r"\sTerrace\s": r" Terr ",
    r"\sThicket\s": r" Thick ",
    r"\sTownline\s": r" Tline ",
    r"\sTR\s": r" Trail ",
    r"\sTurnabout\s": r" Trnabt ",
    r"\sVA\s": r" Vale ",
    r"\sVG\s": r" Villge ",
    r"\sVillage\s": r" Villge ",
    r"\sVI\s": r" Villas ",
    r"\sVS\s": r" Vista ",
    r"\sVW\s": r" View ",
    r"\sWD\s": r" Wynd ",
    r"\sWK\s": r" Walk ",
    r"\sWO\s": r" Wood ",
    r"\sWY\s": r" Way ",
    r"\sXS\s": r" Cross "
}

# Define directions
DIRECTIONS = ['E', 'N', 'W', 'S', 'NE', 'NW', 'SE', 'SW']

def exchange_address_abbreviations(address):
    # Split the address into parts
    parts = re.split(r'(\s+)', address)

    # Find the index of the first comma
    comma_index = None
    for i, part in enumerate(parts):
        if ',' in part:
            comma_index = i
            break

    # Find the index of the direction (search from back to front)
    direction_index = None
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].strip() in DIRECTIONS:
            direction_index = i
            break

    # Determine the index of the word to replace
    if direction_index is not None:
        target_index = direction_index - 2 if direction_index > 0 else None
    elif comma_index is not None:
        target_index = comma_index - 2 if comma_index > 0 else None
    else:
        target_index = len(parts) - 1 if len(parts) > 1 else None

    # Replace the target abbreviation if found
    street_type = None
    if target_index is not None and target_index >= 0:
        for abbrev, full in REPLACEMENTS.items():
            if re.search(abbrev, ' ' + parts[target_index] + ' '):
                parts[target_index] = re.sub(abbrev, full.strip(), ' ' + parts[target_index] + ' ').strip()
                street_type = parts[target_index]                
                break
        if street_type is None:
            target_index = None

    # Prepare the final updated address
    updated_address = ''.join(parts)
    street_quad = parts[direction_index] if direction_index is not None else None

    # Extract the street name excluding replaced_part and direction_part
    street_name_parts = [part for i, part in enumerate(parts) if i != target_index and i != direction_index]
    street_name = ''.join(street_name_parts).strip()


    return updated_address, street_name, street_type, street_quad

# Function to calculate the centroid of a polygon
def calculate_centroid(polygon_wkt):
    polygon = load_wkt(polygon_wkt)
    centroid = polygon.centroid
    return centroid.x, centroid.y

def get_addresses_from_db(cursor, limit, offset):
    # Fetch data from planet_osm_polygon
    cursor.execute("""
        SELECT
            osm_id,
            tags->'addr:street' AS street,
            tags->'addr:postcode' AS postcode,
            tags->'addr:housenumber' AS housenumber,
            ST_X(ST_Centroid(way)) AS longitude,
            ST_Y(ST_Centroid(way)) AS latitude
        FROM
            planet_osm_polygon
        WHERE
            tags ? 'addr:street' AND tags ? 'addr:postcode' AND tags ? 'addr:housenumber'
        LIMIT %s OFFSET %s           
    """, (limit, offset))
    return cursor.fetchall()

# Insert addresses into mrag_ca_addresses table
def insert_addresses(cursor, addresses):
    insert_query = """
        INSERT INTO mrag_ca_addresses (id, street_full_name, street_name, street_type, street_quad, full_address, postal_code, street_no, geo_latitude, geo_longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for address in addresses:
        cursor.execute(insert_query, address)

# Main script
if __name__ == "__main__":
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        limit = 10
        offset = 0

        while True:
            rows = get_addresses_from_db(cursor, limit, offset)
            if not rows:
                break

            addresses = []
            for row in rows:
                id = row['osm_id']
                street_no = row['housenumber']
                street_full_name, street_name, street_type, street_quad = exchange_address_abbreviations(row['street'])
                full_address = street_no + ' ' + street_full_name
                postal_code = row['postcode']                
                geo_latitude = row['latitude']
                geo_longitude = row['longitude']
                address = (id, street_full_name, street_name, street_type, street_quad, full_address, postal_code, street_no, geo_latitude, geo_longitude)
                print(address)
                addresses.append(address)

            insert_addresses(cursor, addresses)
            conn.commit()
            
            offset += limit
            break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
