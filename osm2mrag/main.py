import os
import re
import Levenshtein
from tqdm import tqdm
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
    r"\sAbbey\s": r"Abbey",
    r"\sAcre\s": r"Acres",
    r"\sAcres\s": r"Acres",
    r"\sAl\s": r"Alley",
    r"\sAll\s": r"Alley",
    r"\sAllee\s": r"Alley",
    r"\sAllée\s": r"Alley",
    r"\sAlley\s": r"Alley",
    r"\sAly\s": r"Alley",
    r"\sAut\s": r"Aut",
    r"\sAutoroute\s": r"Aut",
    r"\sAv\s": r"Ave",
    r"\sAve\s": r"Ave",
    r"\sAve.\s": r"Ave",
    r"\sAveneue\s": r"Ave",
    r"\sAvenue\s": r"Ave",
    r"\sAvenue East\s": r"Ave",
    r"\sAvenue Extension\s": r"Ave",
    r"\sAvenue Louth\s": r"Ave",
    r"\sAvenue West\s": r"Ave",
    r"\sAv Cl\s": r"Ave Close",
    r"\sAve Close\s": r"Ave Close",
    r"\sAv Cr\s": r"Ave Cres",
    r"\sAve Cres\s": r"Ave Cres",
    r"\sBa\s": r"Bay",
    r"\sBay\s": r"Bay",
    r"\sCauseway\s": r"Bay",
    r"\sBe\s": r"Beach",
    r"\sBea\s": r"Beach",
    r"\sBeach\s": r"Beach",
    r"\sBend\s": r"Bend",
    r"\sBluff\s": r"Bluff",
    r"\sBluffs\s": r"Bluff",
    r"\sBl\s": r"Blvd",
    r"\sBlvd\s": r"Blvd",
    r"\sBlvd.\s": r"Blvd",
    r"\sBoul\s": r"Blvd",
    r"\sBoulevard\s": r"Blvd",
    r"\sBv\s": r"Blvd",
    r"\sPont\s": r"Boul",
    r"\sBoul\s": r"Boul",
    r"\sBrne\s": r"Bourne",
    r"\sBourne\s": r"Bourne",
    r"\sBrae\s": r"Brae",
    r"\sBr\s": r"Branch",
    r"\sBranch\s": r"Branch",
    r"\sBridge\s": r"Bridge",
    r"\sBy-Pass\s": r"Bypass",
    r"\sBypass\s": r"Bypass",
    r"\sByway\s": r"Byway",
    r"\sCampus\s": r"Campus",
    r"\sCa\s": r"Cape",
    r"\sCape\s": r"Cape",
    r"\sCar\s": r"Carré",
    r"\sCarré\s": r"Carré",
    r"\sCarrefour\s": r"Carref",
    r"\sCarref\s": r"Carref",
    r"\sCul-De-Sac\s": r"Cds",
    r"\sCds\s": r"Cds",
    r"\sCentrale\s": r"Centrale",
    r"\sCercle\s": r"Cercle",
    r"\sCh\s": r"Ch",
    r"\sChemin\s": r"Ch",
    r"\sChart\s": r"Chart",
    r"\sChase\s": r"Chase",
    r"\sCi\s": r"Cir",
    r"\sCir\s": r"Cir",
    r"\sCir.\s": r"Cir",
    r"\sCirc\s": r"Cir",
    r"\sCircle\s": r"Cir",
    r"\sCircuit\s": r"Circt",
    r"\sCirct\s": r"Circt",
    r"\sClimb\s": r"Climb",
    r"\sCl\s": r"Close",
    r"\sClo\s": r"Close",
    r"\sClose\s": r"Close",
    r"\sCls\s": r"Close",
    r"\sCm\s": r"Common",
    r"\sCmn.\s": r"Common",
    r"\sCommon\s": r"Common",
    r"\sConcession\s": r"Concession",
    r"\sConn\s": r"Conn",
    r"\sConnecto\s": r"Conn",
    r"\sCote\s": r"Côte",
    r"\sCôte\s": r"Côte",
    r"\sCours\s": r"Cours",
    r"\sCove\s": r"Cove",
    r"\sCv\s": r"Cove",
    r"\sCr\s": r"Cres",
    r"\sCre\s": r"Cres",
    r"\sCres\s": r"Cres",
    r"\sCres.\s": r"Cres",
    r"\sCrescent\s": r"Cres",
    r"\sCs\s": r"Cres",
    r"\sCrest\s": r"Crest",
    r"\sCrst\s": r"Crest",
    r"\sCnr\s": r"Crnrs",
    r"\sCorner\s": r"Crnrs",
    r"\sCorners\s": r"Crnrs",
    r"\sCrnrs\s": r"Crnrs",
    r"\sCroft\s": r"Croft",
    r"\sCroissant\s": r"Crois",
    r"\sCrois\s": r"Crois",
    r"\sCro\s": r"Cross",
    r"\sCross\s": r"Cross",
    r"\sCrossing\s": r"Cross",
    r"\sCrss\s": r"Cross",
    r"\sCx\s": r"Cross",
    r"\sCrossove\s": r"Crossover",
    r"\sCrover\s": r"Crossover",
    r"\sCrsover\s": r"Crossover",
    r"\sCrossover\s": r"Crossover",
    r"\sCrossway\s": r"Crossway",
    r"\sCo\s": r"Crt",
    r"\sCour\s": r"Crt",
    r"\sCourt\s": r"Crt",
    r"\sCrt\s": r"Crt",
    r"\sCrt.\s": r"Crt",
    r"\sCt\s": r"Crt",
    r"\sCe\s": r"Ctr",
    r"\sCentre\s": r"Ctr",
    r"\sCurve\s": r"Curve",
    r"\sCut\s": r"Cut",
    r"\sDale\s": r"Dale",
    r"\sDell\s": r"Dell",
    r"\sDesserte Est\s": r"Desste",
    r"\sDesserte Nord\s": r"Desste",
    r"\sDesserte Ouest\s": r"Desste",
    r"\sDesserte Sud\s": r"Desste",
    r"\sDiv\s": r"Divers",
    r"\sDivers\s": r"Divers",
    r"\sDiversion\s": r"Divers",
    r"\sDv\s": r"Divers",
    r"\sDowns\s": r"Downs",
    r"\sDr\s": r"Dr",
    r"\sDr.\s": r"Dr",
    r"\sDrive\s": r"Dr",
    r"\sDrive Extension\s": r"Dr Exten",
    r"\sEnd\s": r"End",
    r"\sEspl\s": r"Espl",
    r"\sEsplanade\s": r"Espl",
    r"\sEst\s": r"Estate",
    r"\sEstate\s": r"Estate",
    r"\sEsts\s": r"Estate",
    r"\sEstates\s": r"Estates",
    r"\sEt\s": r"Estates",
    r"\sExpressway\s": r"Expy",
    r"\sExpy\s": r"Expy",
    r"\sExt\s": r"Exten",
    r"\sExten\s": r"Exten",
    r"\sExtension\s": r"Exten",
    r"\sFairway\s": r"Fairway",
    r"\sFarm\s": r"Farm",
    r"\sField\s": r"Field",
    r"\sForest\s": r"Forest",
    r"\sFront\s": r"Front",
    r"\sFsr\s": r"Fsr",
    r"\sFreeway\s": r"Fwy",
    r"\sFwy\s": r"Fwy",
    r"\sGallery\s": r"Gallery",
    r"\sGa\s": r"Gate",
    r"\sGate\s": r"Gate",
    r"\sGt\s": r"Gate",
    r"\sGateway\s": r"Gateway",
    r"\sGtwy\s": r"Gateway",
    r"\sGw\s": r"Gateway",
    r"\sGarden\s": r"Gdns",
    r"\sGardens\s": r"Gdns",
    r"\sGd\s": r"Gdns",
    r"\sGdn\s": r"Gdns",
    r"\sGdns\s": r"Gdns",
    r"\sGs\s": r"Gdns",
    r"\sGlade\s": r"Glade",
    r"\sGl\s": r"Glen",
    r"\sGlen\s": r"Glen",
    r"\sGrange\s": r"Grange",
    r"\sGr\s": r"Green",
    r"\sGre\s": r"Green",
    r"\sGreen\s": r"Green",
    r"\sGrn\s": r"Green",
    r"\sGreenway\s": r"Greenway",
    r"\sGy\s": r"Greenway",
    r"\sGrounds\s": r"Grnds",
    r"\sGrnds\s": r"Grnds",
    r"\sGrove\s": r"Grove",
    r"\sGrv\s": r"Grove",
    r"\sGv\s": r"Grove",
    r"\sHal\s": r"Hall",
    r"\sHall\s": r"Hall",
    r"\sHarbour\s": r"Harbr",
    r"\sHarbr\s": r"Harbr",
    r"\sHaven\s": r"Haven",
    r"\sHe\s": r"Heath",
    r"\sHeath\s": r"Heath",
    r"\sHighlands\s": r"Hghlds",
    r"\sHghlds\s": r"Hghlds",
    r"\sHdwy\s": r"Hideaway",
    r"\sHideaway\s": r"Hideaway",
    r"\sHideway\s": r"Hideaway",
    r"\sHidewy\s": r"Hideaway",
    r"\sHighland\s": r"Highland",
    r"\sHil\s": r"Hill",
    r"\sHill\s": r"Hill",
    r"\sHl\s": r"Hill",
    r"\sHoller\s": r"Holler",
    r"\sHllw\s": r"Hollow",
    r"\sHol\s": r"Hollow",
    r"\sHollow\s": r"Hollow",
    r"\sHeight\s": r"Hts",
    r"\sHeights\s": r"Hts",
    r"\sHt\s": r"Hts",
    r"\sHts\s": r"Hts",
    r"\sHi\s": r"Hwy",
    r"\sHighway\s": r"Hwy",
    r"\sHwy\s": r"Hwy",
    r"\sHwy.\s": r"Hwy",
    r"\sHy\s": r"Hwy",
    r"\sIle\s": r"Ile",
    r"\sÎle\s": r"Île",
    r"\sImp\s": r"Imp",
    r"\sImpasse\s": r"Imp",
    r"\sInl\s": r"Inlet",
    r"\sInlet\s": r"Inlet",
    r"\sIs\s": r"Island",
    r"\sIsland\s": r"Island",
    r"\sIsle\s": r"Isle",
    r"\sJardin\s": r"Jardin",
    r"\sKeep\s": r"Keep",
    r"\sKemew\s": r"Kemew",
    r"\sKey\s": r"Key",
    r"\sKnoll\s": r"Knoll",
    r"\sLake\s": r"Lake",
    r"\sLakeway\s": r"Lakeway",
    r"\sLandg\s": r"Landng",
    r"\sLanding\s": r"Landng",
    r"\sLanng\s": r"Landng",
    r"\sLd\s": r"Landng",
    r"\sLndg\s": r"Landng",
    r"\sAwti\s": r"Lane",
    r"\sAwti'J\s": r"Lane",
    r"\sLa\s": r"Lane",
    r"\sLan\s": r"Lane",
    r"\sLane\s": r"Lane",
    r"\sLn\s": r"Lane",
    r"\sLea\s": r"Lea",
    r"\sLine\s": r"Line",
    r"\sLi\s": r"Link",
    r"\sLink\s": r"Link",
    r"\sLk\s": r"Link",
    r"\sLinkway\s": r"Linkway",
    r"\sLinkwy\s": r"Linkway",
    r"\sLnkwy\s": r"Linkway",
    r"\sLkout\s": r"Lkout",
    r"\sLookout\s": r"Lkout",
    r"\sLimits\s": r"Lmts",
    r"\sLmts\s": r"Lmts",
    r"\sLoop\s": r"Loop",
    r"\sLp\s": r"Loop",
    r"\sMall\s": r"Mall",
    r"\sManor\s": r"Manor",
    r"\sMr\s": r"Manor",
    r"\sMarsh\s": r"Marsh",
    r"\sMaze\s": r"Maze",
    r"\sMeadow\s": r"Meadow",
    r"\sMeadows\s": r"Meadows",
    r"\sMe\s": r"Mews",
    r"\sMews\s": r"Mews",
    r"\sMs\s": r"Mews",
    r"\sMillway\s": r"Millway",
    r"\sMontee\s": r"Montée",
    r"\sMontée\s": r"Montée",
    r"\sMoor\s": r"Moor",
    r"\sMount\s": r"Mount",
    r"\sMt\s": r"Mount",
    r"\sMount\s": r"Mount",
    r"\sMtn\s": r"Mount",
    r"\sOrch\s": r"Orchard",
    r"\sOrchard\s": r"Orchard",
    r"\sOutlook\s": r"Outlook",
    r"\sPa\s": r"Parade",
    r"\sParade\s": r"Parade",
    r"\sPr\s": r"Parade",
    r"\sParc\s": r"Parc",
    r"\sParkland\s": r"Parkland Dr",
    r"\sPass\s": r"Pass",
    r"\sPassage\s": r"Pass",
    r"\sPs\s": r"Pass",
    r"\sPssg\s": r"Pass",
    r"\sPath\s": r"Path",
    r"\sPh\s": r"Path",
    r"\sPth\s": r"Path",
    r"\sPtway\s": r"Pathway",
    r"\sPathway\s": r"Pathway",
    r"\sPines\s": r"Pines",
    r"\sPark\s": r"Pk",
    r"\sPk\s": r"Pk",
    r"\sParkway\s": r"Pky",
    r"\sPkwy\s": r"Pky",
    r"\sPky\s": r"Pky",
    r"\sPpky\s": r"Pky",
    r"\sPw\s": r"Pky",
    r"\sPy\s": r"Pky",
    r"\sPl\s": r"Pl",
    r"\sPl.\s": r"Pl",
    r"\sPla\s": r"Pl",
    r"\sPlace\s": r"Pl",
    r"\sPlateau\s": r"Plat",
    r"\sPlat\s": r"Plat",
    r"\sPlaza\s": r"Plaza",
    r"\sPlz\s": r"Plaza",
    r"\sPz\s": r"Plaza",
    r"\sPond\s": r"Pond",
    r"\sPort\s": r"Port",
    r"\sProm\s": r"Prom",
    r"\sPromenade\s": r"Prom",
    r"\sPoint\s": r"Pt",
    r"\sPointe\s": r"Pt",
    r"\sPt\s": r"Pt",
    r"\sPathway\s": r"Ptway",
    r"\sPtway\s": r"Ptway",
    r"\sPrivate\s": r"Pvt",
    r"\sPvt\s": r"Pvt",
    r"\sQuai\s": r"Quai",
    r"\sQuay\s": r"Quay",
    r"\sRailway\s": r"Railway",
    r"\sRamp\s": r"Ramp",
    r"\sRp\s": r"Ramp",
    r"\sRang\s": r"Rang",
    r"\sRange\s": r"Rang",
    r"\sRd\s": r"Rd",
    r"\sRd.\s": r"Rd",
    r"\sRdfork\s": r"Rd",
    r"\sRoad\s": r"Rd",
    r"\sReach\s": r"Reach",
    r"\sRge Rd\s": r"Rge Rd",
    r"\sRg\s": r"Ridge",
    r"\sRid\s": r"Ridge",
    r"\sRidge\s": r"Ridge ",
    r"\sRi\s": r"Rise",
    r"\sRise\s": r"Rise",
    r"\sRiver\s": r"River",
    r"\sRle\s": r"Rle",
    r"\sRuelle\s": r"Rle",
    r"\sRoadway\s": r"Roadway",
    r"\sRound\s": r"Round",
    r"\sRo\s": r"Row",
    r"\sRow\s": r"Row",
    r"\sRoute\s": r"Rte",
    r"\sRte\s": r"Rte",
    r"\sRue\s": r"Rue",
    r"\sRun\s": r"Run",
    r"\sShore\s": r"Shore",
    r"\sShoreline\s": r"Shoreline",
    r"\sShores\s": r"Shores",
    r"\sSideline\s": r"Sideline",
    r"\sSdrd\s": r"Siderd",
    r"\sSiderd\s": r"Siderd",
    r"\sSide Rd\s": r"Siderd",
    r"\sSideroad\s": r"Siderd",
    r"\sSr\s": r"Siderd",
    r"\sSrd\s": r"Siderd",
    r"\sSprings\s": r"Springs",
    r"\sSpur\s": r"Spur",
    r"\sSq\s": r"Sq",
    r"\sSquare\s": r"Sq",
    r"\sSt\s": r"St",
    r"\sSt.\s": r"St",
    r"\sStreet\s": r"St",
    r"\sSt Cl\s": r"St Close",
    r"\sSt Close\s": r"St Close",
    r"\sSt Cr\s": r"St Cres",
    r"\sSt Cres\s": r"St Cres",
    r"\sStreet Extension\s": r"St Exten",
    r"\sSt Exten\s": r"St Exten",
    r"\sStreet Louth\s": r"St Louth",
    r"\sSt Louth\s": r"St Louth",
    r"\sSt Dr\s": r"Street Dr",
    r"\sStreet Dr\s": r"Street Dr",
    r"\sStrip\s": r"Strip",
    r"\sSubdivision\s": r"Subdiv",
    r"\sSubdiv\s": r"Subdiv",
    r"\sTc\s": r"Terr",
    r"\sTe\s": r"Terr",
    r"\sTer\s": r"Terr",
    r"\sTerr\s": r"Terr",
    r"\sTerr.\s": r"Terr",
    r"\sTerrace\s": r"Terr",
    r"\sThicket\s": r"Thick",
    r"\sThick\s": r"Thick",
    r"\sTl\s": r"Tline",
    r"\sTline\s": r"Tline",
    r"\sTownline\s": r"Tline",
    r"\sTop\s": r"Top",
    r"\sTowers\s": r"Towers",
    r"\sTrace\s": r"Trace",
    r"\sTr\s": r"Trail",
    r"\sTra\s": r"Trail",
    r"\sTrail\s": r"Trail",
    r"\sTrl\s": r"Trail",
    r"\sTurnabout\s": r"Trnabt",
    r"\sTrnabt\s": r"Trnabt",
    r"\sTerrasse\s": r"Tsse",
    r"\sTsse\s": r"Tsse",
    r"\sTunnel\s": r"Tunnel",
    r"\sTrn\s": r"Turn",
    r"\sTurn\s": r"Turn",
    r"\sTwp Rd\s": r"Twp Rd",
    r"\sUn\s": r"Un",
    r"\sUnion\s": r"Union",
    r"\sVale\s": r"Vale",
    r"\sVia\s": r"Via",
    r"\sView\s": r"View",
    r"\sVw\s": r"View",
    r"\sVi\s": r"Villas",
    r"\sVillas\s": r"Villas",
    r"\sVillage\s": r"Villge",
    r"\sVillge\s": r"Villge",
    r"\sVista\s": r"Vista",
    r"\sVoie\s": r"Voie",
    r"\sWalk\s": r"Walk",
    r"\sWk\s": r"Walk",
    r"\sWlk\s": r"Walk",
    r"\sWalkway\s": r"Walkway",
    r"\sWa\s": r"Water Access",
    r"\sWatacc\s": r"Water Access",
    r"\sWater Ac\s": r"Water Access",
    r"\sWater Access\s": r"Water Access",
    r"\sWaterway\s": r"Waterway",
    r"\sWw\s": r"Waterway",
    r"\sWay\s": r"Way",
    r"\sWy\s": r"Way",
    r"\sWestway\s": r"West Way",
    r"\sWest Way\s": r"West Way",
    r"\sWharf\s": r"Wharf",
    r"\sWillow\s": r"Willow",
    r"\sWds\s": r"Wood",
    r"\sWood\s": r"Wood",
    r"\sWoods\s": r"Woods",
    r"\sWynd\s": r"Wynd",
    r"\sWynde\s": r"Wynd",
    r"\sNot Appl\s": r"",
}

# Define directions
DIRECTIONS = ['E', 'N', 'W', 'S', 'NE', 'NW', 'SE', 'SW']

DIRECTIONS_REPLACEMENTS = {
        r'\beast\b$': 'E',
        r'\bnorth\b$': 'N',
        r'\bnorth[\s-]?east\b$': 'NE',
        r'\bnorth[\s-]?west\b$': 'NW',
        r'\bsouth\b$': 'S',
        r'\bsouth[\s-]?east\b$': 'SE',
        r'\bsouth[\s-]?west\b$': 'SW',
        r'\bwest\b$': 'W',
        r'\bwst\b$': 'W',
    }

def convert_direction(address):
    for pattern, replacement in DIRECTIONS_REPLACEMENTS.items():
        if re.search(pattern, address, re.IGNORECASE):
            address = re.sub(pattern, replacement, address, flags=re.IGNORECASE)
            break

    return address

def format_postal_code(postal_code):
    if postal_code is not None:
        # Remove any existing spaces
        postal_code = postal_code.replace(' ', '')

        # Format the postal code if it has at least 6 characters
        if len(postal_code) >= 6:
            formatted_postal_code = postal_code[:3].upper() + ' ' + postal_code[3:6].upper()
        else:
            # Ensure the postal code is in uppercase if it's incomplete
            formatted_postal_code = postal_code.upper()
        
        return formatted_postal_code
    return None

def exchange_address_abbreviations(address):
    address = convert_direction(address)
    
    # Split the address into parts
    parts = re.split(r'(\s+)', address)
    
    # Initialize variables
    comma_index = None
    direction_index = None
    target_index = None
    street_type = None
    style = 'English'

    # Find the index of the first comma
    for i, part in enumerate(parts):
        if ',' in part:
            comma_index = i
            break 

    # Find the index of the direction (search from back to front)
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].strip() in DIRECTIONS:
            direction_index = i
            break
        
    # Determine the starting index for the backward search
    start_index = comma_index if comma_index is not None else len(parts) - 1    
        
    # Determine the index of the word to replace (search from back to front)
    for i in range(start_index, -1, -1):
        for abbrev in REPLACEMENTS.keys():
            if re.search(abbrev, ' ' + parts[i].strip() + ' '):
                if target_index is not None:
                    # If another replacement is found, assume English style
                    style = 'English'
                    break
                target_index = i
        if target_index is not None:
            break

    # Detect French style based on the replacement part position
    if target_index is not None and target_index < start_index and (direction_index is None or target_index != direction_index - 2):
        style = 'French'

    # Replace the target abbreviation if found
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
            tags->'addr:state' AS state,
            tags->'addr:province' AS province,
            tags->'addr:city' AS city,
            ST_X(ST_Centroid(way)) AS longitude,
            ST_Y(ST_Centroid(way)) AS latitude,
            way
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
        INSERT INTO mrag_ca_addresses (id, street_full_name, street_name, street_type, street_quad, full_address, postal_code, geo_latitude, geo_longitude, boundary, region, city, street_no, house_number, house_alpha, unit)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            street_full_name = EXCLUDED.street_full_name,
            street_name = EXCLUDED.street_name,
            street_type = EXCLUDED.street_type,
            street_quad = EXCLUDED.street_quad,
            full_address = EXCLUDED.full_address,
            postal_code = EXCLUDED.postal_code,
            street_no = EXCLUDED.street_no,
            house_number = EXCLUDED.house_number, 
            house_alpha = EXCLUDED.house_alpha,
            unit = EXCLUDED.unit,
            geo_latitude = EXCLUDED.geo_latitude,
            geo_longitude = EXCLUDED.geo_longitude,
            boundary = EXCLUDED.boundary,
            region = EXCLUDED.region,
            city = EXCLUDED.city;
    """
    for address in addresses:
        try:
            cursor.execute("SAVEPOINT before_insert")
            cursor.execute(insert_query, address)
        except Exception as e:
            print(address)
            print(f"Error: {e}")
            cursor.execute("ROLLBACK TO SAVEPOINT before_insert")
        
# Function to check and set region and city based on boundaries
def check_and_set_region_city(cursor, latitude, longitude):
    query = """
    SELECT name, place, bound
    FROM mrag_boundary_data
    WHERE ST_Contains(bound, ST_SetSRID(ST_Point(%s, %s), 4326))
    """
    cursor.execute(query, (longitude, latitude))
    results = cursor.fetchall()
    
    region = None
    city = None

    for result in results:
        if result['place'] == 'state':
            region = result['name']
        else:
            city = result['name']

    return region, city        

def extract_parts(house_no, street_name):
    def clean_and_split(input_str):
        input_str = input_str.strip().replace('"', '').replace("'", "").replace('`', '')
        parts = re.split(r'[;,/&\-]', input_str)        
        if (match := re.match(r'^(\d+\w*)\s+((\d+\w*\s+)+\d+\w*)$', house_no)): 
            parts = [match.group(1)]  # extract first item of 1 2 3 4 5
        elif(len(parts) == 2 and bool(re.search(r'^\d+\s+1\/2$', input_str))): 
            parts = [input_str.strip()] # for cases like: "11 1/2"
        elif(len(parts) == 2 and bool(re.search(r',', input_str))):
            parts = [input_str.strip()]
        elif(len(parts) == 2 and bool(re.search(r'\S-\S', input_str))) or (len(parts) == 2 and bool(re.search(r'\S-$', input_str))):
            parts = [input_str.strip()]
        else:
            parts = [part.strip() for part in parts if part.strip()]  
        return parts

    def find_difference_position(s1, s2):
        len1, len2 = len(s1), len(s2)
        min_len = min(len1, len2)        
        # Find the first position where the characters differ
        for i in range(min_len):
            if s1[i] != s2[i]:
                return i        
        # If no difference is found in the overlapping part, check the lengths
        if len1 != len2:
            return min_len        
        return -1
    
    def process_house_no(house_no):
        if not house_no:
            return None, None, None
        house_no = house_no.strip().upper()
        unit_number = None
        number_part = None
        alpha_part = None

        # Handle unit number
        if (match := re.match(r'^(\d+)\s+1\/2$', house_no, re.IGNORECASE)): # for cases like: "11 1/2"
            parts = match.groups()          
            house_no = parts[0] + " ½"
        elif (match := re.match(r'^([\d|\w]+)[\-\s]+(\d+\w?)$', house_no, re.IGNORECASE)):
            parts = match.groups()
            unit_number = parts[0]
            house_no = parts[1]
        elif (match := re.match(r'^(\d+\w?),(\d+\w?)$', house_no, re.IGNORECASE)): # for cases like: "103A,103B"
            parts = match.groups()
            s1 = parts[0]
            s2 = parts[1]
            if Levenshtein.distance(s1, s2) <= 1:
                house_no = s1
            else:
                unit_number = s1
                house_no = s2
        elif (match := re.match(r'^([^,]+\S),(\S[^,]+)$', house_no, re.IGNORECASE)): # for cases like: "1206 1,1206 2"
            parts = match.groups()
            s1 = parts[0]
            s2 = parts[1]
            if Levenshtein.distance(s1, s2) <= 1:
                cut_pos = find_difference_position(s1, s2)
                if cut_pos > -1:
                    house_no = s1[:cut_pos].strip()
                    unit_number = s1[cut_pos:].strip()
                else:
                    house_no = s1
            else:
                unit_number = s1
                house_no = s2
        elif (match := re.match(r'^([\d|\w]+),\s+(\d+\w?).*$', house_no, re.IGNORECASE)):
            parts = match.groups()
            unit_number = parts[0]           
            house_no = parts[1]
        elif (match := re.match(r'^([^-]+)-\s*$', house_no, re.IGNORECASE)):
            parts = match.groups()
            unit_number = parts[0]     
        elif (match := re.match(r'^unit\s*(\S*)([,\-\s]\s*(\d+\s*\w?))?', house_no, re.IGNORECASE)):
            parts = match.groups()
            unit_number = parts[0]
            if len(parts) > 2:
                house_no = parts[2]
            else:
                house_no = None
        elif (match := re.match(r'^(\d+\s*\w?)([,\s]+unit\s*(\S*))', house_no, re.IGNORECASE)): 
            parts = match.groups()
            house_no = parts[0]
            if len(parts) > 2:
                unit_number = parts[2]
        elif (match := re.match(r'^#([^,\-\s]+)([,\-\s]\s*(\d+\s*\w?))?', house_no, re.IGNORECASE)):
            parts = match.groups()
            unit_number = parts[0]            
            if len(parts) > 2:
                house_no = parts[2]
            else:
                house_no = None
        elif (match := re.match(r'^(,\s*)(\d+\s*\w?)', house_no, re.IGNORECASE)):
            parts = match.groups()           
            if len(parts) > 1:
                house_no = parts[1]
        elif (match := re.match(r'^([^\.]+)\.\.\.[^-]+-(\S*)', house_no, re.IGNORECASE)):
            parts = match.groups()
            unit_number = parts[0]
            house_no = parts[1]
        elif (match := re.match(r'^(\d+\s*\w?)\s+([^-]+)-(\S+)$', house_no, re.IGNORECASE)):
            parts = match.groups()
            house_no = parts[0]
            unit_number = parts[1]
                    
        # Handle parentheses
        if house_no:       
            if re.search(r'(\d+\s*\([\d+|\w+]\)?|\d+\s*\[[\d+|\w+]\]?)', house_no):
                number_part = re.findall(r'\d+', house_no.split('(')[0])[0]
                alpha_part = re.findall(r'\d+|\w+', house_no.split('(')[1])[0]
            else:
                # Handle 0.x and .x cases
                if (match := re.match(r'^[0\s]*\.(\d+)$', house_no)):
                    number_part = match.groups()[0]
                # Handle x.x and x.5 cases
                elif re.match(r'^\d+\.\d+$', house_no):
                    number_part, alpha_part = house_no.split('.')
                    alpha_part = '.' + alpha_part
                elif (match:= re.match(r'^(\d+)(\w*)$|^(\d+)\s(\w)$|^(\d+)\s+([\w\s]{2,})$', house_no)):
                    street_parts = match.groups()
                    if street_parts[0] is not None:
                        number_part = street_parts[0].strip()
                        if street_parts[1] is not None:
                            alpha_part = street_parts[1].strip()

                    if street_parts[2] is not None:
                        number_part = street_parts[2].strip()                      
                        if street_parts[3] is not None:
                            alpha_part = street_parts[3].strip()
                    if street_parts[4] is not None:
                        number_part = street_parts[4].strip()

            # Convert alpha part to uppercase
            alpha_part = alpha_part.upper() if alpha_part else None

        return unit_number, number_part, alpha_part

    # Clean and split the house_no string
    parts = clean_and_split(house_no)

    # Process the cleaned parts
    unit_number, number_part, alpha_part = process_house_no(parts[0])

    # Handle specific case for extracting house number and alpha part from street name
    if street_name and (number_part == "" or number_part is None):
        street_match = re.match(r'\s*(\d+)\s*(\w{1})?(\s+\S*)?', street_name)
        if street_match:
            street_parts = street_match.groups()
            number_part = street_parts[0].strip()
            if street_parts[1] is not None:
                alpha_part = street_parts[1].strip()

    return unit_number, number_part, alpha_part

# Main script
if __name__ == "__main__":
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        limit = 1000
        offset = 0
        
        # Initialize total_rows for the progress bar
        cursor.execute("SELECT COUNT(*) FROM planet_osm_polygon WHERE tags ? 'addr:street' AND tags ? 'addr:postcode' AND tags ? 'addr:housenumber'")
        total_rows = cursor.fetchone()['count'] - offset

        with tqdm(total=total_rows, desc="Processing addresses") as pbar:
            while True:
                rows = get_addresses_from_db(cursor, limit, offset)
                if not rows:
                    break

                addresses = []
                for row in rows:
                    id = row['osm_id']
                    street_no = row['housenumber']
                    street = row['street']
                    street_full_name, street_name, street_type, street_quad = exchange_address_abbreviations(row['street'])
                    full_address = street_no + ' ' + street_full_name
                    postal_code = format_postal_code(row['postcode'])                
                    geo_latitude = row['latitude']
                    geo_longitude = row['longitude']
                    boundary = row['way']

                    unit, house_number, house_alpha = extract_parts(street_no, street)
                    if house_alpha is not None and house_alpha.isalpha():
                        street_no = house_number.strip() + house_alpha.strip()
                    elif house_alpha is not None:
                        street_no = house_number.strip() + "(" + house_alpha.strip() + ")"
                    elif house_number is not None:
                        street_no = house_number.strip()
                    else:
                        street_no = None

                    # Determine region
                    state = row['state'] if 'state' in row and row['state'] else None
                    province = row['province'] if 'province' in row and row['province'] else None
                    region = state if state else province
                    
                    city = row['city'] if 'city' in row else None
                    
                    if city is None and region is None:
                        region, city = check_and_set_region_city(cursor, geo_latitude, geo_longitude)
                    
                    address = (id, street_full_name, street_name, street_type, street_quad, full_address, postal_code, geo_latitude, geo_longitude, boundary, region, city, street_no, house_number, house_alpha, unit)
                    addresses.append(address)

                insert_addresses(cursor, addresses)
                conn.commit()
                
                offset += limit
                pbar.update(len(rows))

    except Exception as e:
        print(addresses)
        print(f"Error: {e}")
        print(f"Offset: {offset}")        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
