''' Google Sheets Schemas '''

from typing import List, Dict
from pydantic import BaseModel

class RowMetadata(BaseModel):
    sheet: str
    row: int
    columns: int

class RowData(BaseModel):
    sheet_name: str
    row_number: int
    content: str
    raw_data: List[str]
    metadata: RowMetadata

class GoogleSheetResponse(BaseModel):
    spreadsheet_title: str
    spreadsheet_id: str
    sheet_data: List[RowData]