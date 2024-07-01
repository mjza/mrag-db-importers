import os
import re
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2

# Load environment variables from .env file
load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')  # Path to chromedriver.exe
CONN = psycopg2.connect(
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


# Database connection and pagination
def get_addresses_from_db(limit=1000, offset=0):    
    cur = CONN.cursor()
    cur.execute(
            f"""
                SELECT DISTINCT 
                concat(
                    street_no, 
                    ' ', 
                    street_full_name, ', ', city, ', ', 
                    CASE 
                        WHEN region = 'Alberta' THEN 'AB'
                        WHEN region = 'British Columbia' THEN 'BC'
                        WHEN region = 'Manitoba' THEN 'MB'
                        WHEN region = 'New Brunswick' THEN 'NB'
                        WHEN region = 'Northwest Territories' THEN 'NT'
                        WHEN region = 'Nova Scotia' THEN 'NS'
                        WHEN region = 'Ontario' THEN 'ON'
                        WHEN region = 'Prince Edward Island' THEN 'PE'
                        WHEN region = 'Quebec' THEN 'QC'
                        WHEN region = 'Saskatchewan' THEN 'SK'
                        WHEN region = 'Newfoundland and Labrador' THEN 'NL'
                        WHEN region = 'Yukon' THEN 'YT'
                        WHEN region = 'Nunavut' THEN 'NU'
                        ELSE region
                    END
                ) as address, 
                street_no, 
                street_full_name, 
                concat (street_no, ' ', street_full_name) as full_address,
            concat (city, ', ', 
                CASE 
                    WHEN region = 'Alberta' THEN 'AB'
                    WHEN region = 'British Columbia' THEN 'BC'
                    WHEN region = 'Manitoba' THEN 'MB'
                    WHEN region = 'New Brunswick' THEN 'NB'
                    WHEN region = 'Northwest Territories' THEN 'NT'
                    WHEN region = 'Nova Scotia' THEN 'NS'
                    WHEN region = 'Ontario' THEN 'ON'
                    WHEN region = 'Prince Edward Island' THEN 'PE'
                    WHEN region = 'Quebec' THEN 'QC'
                    WHEN region = 'Saskatchewan' THEN 'SK'
                    WHEN region = 'Newfoundland and Labrador' THEN 'NL'
                    WHEN region = 'Yukon' THEN 'YT'
                    WHEN region = 'Nunavut' THEN 'NU'
                    ELSE region
                END,
             ', ') as city_region,
            city, 
            region
        FROM public.mrag_ca_addresses
        WHERE postal_code IS NULL AND is_valid = true AND region = 'Alberta' AND city = 'Calgary'
        ORDER BY full_address DESC
        LIMIT {limit} OFFSET {offset}
    """)
    addresses = cur.fetchall()
    cur.close()
    return addresses

def update_postal_code_in_db(street_no, street_full_name, city, region, postal_code):
    cur = CONN.cursor()
    if postal_code == None:
        cur.execute("""
            UPDATE public.mrag_ca_addresses 
            SET is_valid = %s 
            WHERE street_no = %s 
            AND street_full_name = %s 
            AND city = %s 
            AND region = %s
        """, (False, street_no, street_full_name, city, region))
    else:
        cur.execute("""
            UPDATE public.mrag_ca_addresses 
            SET postal_code = %s 
            WHERE street_no = %s 
            AND street_full_name = %s 
            AND city = %s 
            AND region = %s
        """, (postal_code, street_no, street_full_name, city, region))

    CONN.commit()
    cur.close()

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    # options.headless = True
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def expand_address_abbreviations(address):
    # Split the address into parts
    parts = re.split(r'(\s+)', address)

    # Find the index of the first comma
    comma_index = None
    for i, part in enumerate(parts):
        if ',' in part:
            comma_index = i
            break

    # Find the index of the direction
    direction_index = None
    for i, part in enumerate(parts):
        if part.strip() in DIRECTIONS:
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
    if target_index is not None and target_index >= 0:
        for abbrev, full in REPLACEMENTS.items():
            if re.search(abbrev, ' ' + parts[target_index] + ' '):
                parts[target_index] = re.sub(abbrev, full.strip(), ' ' + parts[target_index] + ' ').strip()
                break

    return ''.join(parts)

def get_postal_code(driver, address, full_address, street_full_name, city_region):
    target_url = "https://www.canadapost-postescanada.ca/ac/"

    # Check if the page is already loaded
    if driver.current_url != target_url:
        driver.get(target_url)
        time.sleep(3)  # Allow time for the page to load
        
    # Expand abbreviations in the address
    address = expand_address_abbreviations(address)
    full_address = expand_address_abbreviations(full_address)    
    street_full_name = expand_address_abbreviations(street_full_name)
    
    search_box = driver.find_element(By.CSS_SELECTOR, "#address-search")
    search_box.clear()
    driver.execute_script("arguments[0].value = arguments[1];", search_box, address)
    search_box.send_keys(Keys.SPACE);    
    time.sleep(1)  # Allow time for the dropdown to populate
    
    try:
        # Wait until the parent element is present
        parent_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#top > div.pca > div:nth-child(1) > div.pca.pcalist"))
        )

        # Find all .pcaitem elements within the parent element
        items = parent_element.find_elements(By.CSS_SELECTOR, ".pcaitem")
        full_address = full_address.strip().lower()
        for item in items:
            title = item.get_attribute("title").strip().lower()
            # Check if the title matches the full address and the description starts with the city_region            
            if full_address in title or title == street_full_name.strip().lower():
                description = item.find_element(By.CSS_SELECTOR, ".pcadescription").text
                if city_region in description:
                    pattern = f"^.*{re.escape(city_region)}"
                    description = re.sub(pattern, "", description).strip()
                    # Regex pattern to match the postal code format at the end of the string
                    match = re.search(r"^(\w{3}\s\w{3})\s*", description)
                    if match:
                        postal_code = match.group(0)
                        return postal_code
    except Exception as e:
        print(f"Error fetching postal code for {address}: {e}")
        return None

    return None  # Return None if no postal code is found

if __name__ == "__main__":
    driver = create_driver()
    limit = 10
    offset = 0

    while True:
        addresses = get_addresses_from_db(limit, offset)
        if not addresses:
            break

        for address, street_no, street_full_name, full_address, city_region, city, region in addresses:
            print(f"Fetching postal code for: {address}")
            postal_code = get_postal_code(driver, address, full_address, street_full_name, city_region)
            if postal_code:
                print(f"Found postal code: {postal_code} for address: {address}")
                update_postal_code_in_db(street_no, street_full_name, city, region, postal_code)
            else:
                print(f"Could not find postal code for address: {address}")
            
        offset += limit

    driver.quit()
