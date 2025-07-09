''' Google Integration Module '''

from python_utils.logging.logging import init_logger

from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.paths import GOOGLE_CREDENTIALS_PATH, SERVICE_CONFIG_PATH
from app.schemas.config import ServiceConfig
from app.schemas.google_sheets import GoogleSheetResponse

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

async def read_google_sheets() -> GoogleSheetResponse:
    '''
    Description: Read data from Google Sheets

    Args:
        None

    Returns:
        spreadsheet_data (GoogleSheetResponse): Spreadsheet metadata
    '''
    logger.info(f"Testing connection to Google Sheets: {SPREADSHEET_ID}")
    
    try:
        
        # Get spreadsheet metadata
        sheet = google_sheets_service.spreadsheets()
        metadata = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        
        # Get spreadsheet title
        title = metadata.get('properties', {}).get('title', 'Unknown')
        logger.info(f"Successfully fetched title: {title}")

        # Get spreadsheet sheets
        sheets = metadata.get('sheets', [])
        sheet_names = [sheet.get('properties', {}).get('title', 'Unknown') for sheet in sheets]
        logger.info(f"Found {len(sheet_names)} sheets in spreadsheet")

        # Batch read data from each sheet
        ranges = [f"{sheet_name}!A:K" for sheet_name in sheet_names]
        data_response = sheet.values().batchGet(
            spreadsheetId=SPREADSHEET_ID,
            ranges=ranges
        ).execute()

        # Fetch and process all row data
        all_row_data = []
        value_ranges = data_response.get('valueRanges', [])
        
        for i, value_range in enumerate(value_ranges):
            sheet_name = sheet_names[i]
            values = value_range.get('values', [])
            
            for row_index, row in enumerate(values):
                row_data = {
                    'sheet_name': sheet_name,
                    'row_number': row_index + 1,
                    'content': ' | '.join(str(cell) for cell in row),
                    'raw_data': row,
                    'metadata': {
                        'sheet': sheet_name,
                        'row': row_index + 1,
                        'columns': len(row)
                    }
                }
                all_row_data.append(row_data)

        logger.info(f"Successfully fetched {len(all_row_data)} rows from {len(sheet_names)} sheets")
        
        return GoogleSheetResponse(
            spreadsheet_title=title,
            spreadsheet_id=SPREADSHEET_ID,
            sheets_data=all_row_data
        )
        
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        raise