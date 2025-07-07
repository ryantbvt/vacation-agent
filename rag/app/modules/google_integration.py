''' Google Integration Module '''

from python_utils.logging.logging import init_logger

from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.paths import GOOGLE_CREDENTIALS_PATH, SERVICE_CONFIG_PATH
from app.schemas.config import ServiceConfig

# Initialize logger
logger = init_logger()

# Initialize Google Sheets Config
config = ServiceConfig.from_yaml(SERVICE_CONFIG_PATH).google_sheets
SPREADSHEET_ID = config.sheet_id

# Read mounted file
creds_path = GOOGLE_CREDENTIALS_PATH
credentials = service_account.Credentials.from_service_account_file(
    creds_path,
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)

# Initialize Google Sheets API
google_sheets_service = build(
    "sheets",
    "v4",
    credentials=credentials
)

logger.info(f"Connected to Google Sheets API: {SPREADSHEET_ID}")

async def read_google_sheets():
    '''
    Description: Read data from Google Sheets

    Args:
        TODO
    '''
    logger.info(f"Testing connection to Google Sheets: {SPREADSHEET_ID}")
    
    try:
        # Just get basic spreadsheet info to test connection
        sheet = google_sheets_service.spreadsheets()
        metadata = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        
        title = metadata.get('properties', {}).get('title', 'Unknown')
        logger.info(f"Successfully connected to spreadsheet: {title}")
        return title
        
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        raise