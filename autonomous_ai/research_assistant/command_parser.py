"""Natural language experiment command parser foundation."""

class CommandParser:
    def parse(self, text):
        return {
            "goal": text,
            "parameters": {},
            "requires_planning": True
        }
