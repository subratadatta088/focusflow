from .base import EvalType

class URLWhitelistRule(EvalType):
    def evaluate(self, context) -> int:
        browsing_data = context.get("browser", {})
        points = 0

        for domain in self.rule["target"]:
            visit_minutes = browsing_data.get(domain, 0)
            interval = self.rule["points"]["interval"]
            value = self.rule["points"]["value"]

            points += (visit_minutes // interval) * value

        return points
