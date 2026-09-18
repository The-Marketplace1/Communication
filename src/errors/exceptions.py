"""Stable application errors mapped by the HTTP layer."""
class CommunicationError(Exception):
    """Base class for expected service errors."""
    code = "communication_error"
    status = 400
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
class InternalError(CommunicationError):
    code = "internal_error"
    status = 500
class ValidationError(CommunicationError):
    code = "validation_error"
    status = 422
class AuthenticationError(CommunicationError):
    code = "authentication_required"
    status = 401
class AuthorizationError(CommunicationError):
    code = "forbidden"
    status = 403
class NotFoundError(CommunicationError):
    code = "not_found"
    status = 404
class ConflictError(CommunicationError):
    code = "conflict"
    status = 409
class ProviderError(CommunicationError):
    code = "provider_error"
    status = 502
class AbuseError(CommunicationError):
    code = "abuse_limit_exceeded"
    status = 429

