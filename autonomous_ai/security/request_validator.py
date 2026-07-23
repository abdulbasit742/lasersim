"""API request validation foundation."""

class RequestValidator:
    def validate(self, request: dict) -> bool:
        return bool(request)
