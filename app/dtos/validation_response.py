import json


class ValidationResponse:
    is_valid: bool
    details: str

    def __init__(self, is_valid: bool, details: str = ''):
        self.is_valid = is_valid
        self.details = details

    def to_JSON(self):
        return json.dumps({
            "is_valid": self.is_valid,
            "details": self.details
        })
