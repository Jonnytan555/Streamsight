import os
from appsettings import *  # noqa: F401,F403
from utils.db import build_engine

SOURCE_NAME              = "ensog"
SOURCE_TYPE              = "database"
SOURCE_TABLE             = "ENTSOGUrgentMarketMessages"
MARKET_REGION            = "Europe"
SECTOR                   = "Energy"
COMMODITY_GROUP          = "Natural Gas"
COMMODITY_CLASSIFICATION = "European Gas"
COMMODITY_NAME           = None

SCRAPE_DB_SERVER = "PRD-DB-SQL-208" if os.getenv("SERVER") == "PRD" else "localhost"

DB_ENGINE  = build_engine(server=SCRAPE_DB_SERVER, database="Scrape")
SOURCE_URL = f"mssql://{SCRAPE_DB_SERVER}/Scrape/dbo/{SOURCE_TABLE}"
