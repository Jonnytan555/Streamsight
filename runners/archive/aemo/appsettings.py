import sqlalchemy as sa
from appsettings import *  # noqa: F401,F403

SOURCE_NAME              = "aemo"
SOURCE_TYPE              = "database"
SOURCE_TABLE             = "AEMOActualFlowsAustralia"
MARKET_REGION            = "Australia"
SECTOR                   = "Energy"
COMMODITY_GROUP          = "Natural Gas"
COMMODITY_CLASSIFICATION = "Australian Gas"
COMMODITY_NAME           = "AEMO"

DB_SERVER = "localhost"
DB_NAME   = "Scrape"
DB_DRIVER = "ODBC Driver 17 for SQL Server"
DB_ENGINE = sa.create_engine(
    f"mssql+pyodbc://{DB_SERVER}/{DB_NAME}"
    f"?driver={DB_DRIVER.replace(' ', '+')}"
)

SOURCE_URL = f"mssql://{DB_SERVER}/{DB_NAME}/dbo/{SOURCE_TABLE}"
