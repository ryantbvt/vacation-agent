''' Google Sheets Schemas '''

from typing import List, Dict
from pydantic import BaseModel

class RowData(BaseModel):
    pass

class GoogleSheetResponse(BaseModel):
    spreadsheet_title: str
    spreadsheet_id: str
    sheet_data: List[RowData]