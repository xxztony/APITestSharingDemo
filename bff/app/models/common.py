from typing import Any


class ServiceError(Exception):
    def __init__(self, error_code: str, message: str, details: dict | None = None, status_code: int = 502):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


def success_response(data: Any) -> dict:
    return {"success": True, "data": data}


def error_payload(error_code: str, message: str, details: dict | None = None) -> dict:
    return {
        "success": False,
        "errorCode": error_code,
        "message": message,
        "details": details or {},
    }

