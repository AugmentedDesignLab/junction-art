from enum import Enum

class CountryCodes(Enum):

    US = "US"
    UK = "UK"

    @staticmethod
    def getByStr(codeStr):
        if codeStr == "US":
            return CountryCodes.US
        if codeStr == "UK":
            return CountryCodes.UK