from fastapi import HTTPException
from typing import Any, Dict, Optional


class CustomHTTPException(HTTPException):
    """Custom HTTP exception with additional context"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.context = context or {}


class ValidationError(CustomHTTPException):
    """Validation error exception"""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            status_code=422,
            detail=detail,
            context={"field": field}
        )


class NotFoundError(CustomHTTPException):
    """Not found error exception"""
    
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        detail = f"{resource} not found"
        if resource_id:
            detail += f" with id: {resource_id}"
        
        super().__init__(
            status_code=404,
            detail=detail,
            context={"resource": resource, "resource_id": resource_id}
        )


class UnauthorizedError(CustomHTTPException):
    """Unauthorized error exception"""
    
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(CustomHTTPException):
    """Forbidden error exception"""
    
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)


class InternalServerError(CustomHTTPException):
    """Internal server error exception"""
    
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=500, detail=detail)
