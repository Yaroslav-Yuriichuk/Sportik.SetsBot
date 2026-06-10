import gspread


class WorksheetProvider:
    def __init__(self, client: gspread.Client) -> None:
        self._client = client

    def get(self, sheet_id: str, worksheet_name: str) -> gspread.Worksheet:
        spreadsheet = self._client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        return worksheet