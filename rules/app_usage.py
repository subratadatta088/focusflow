from .base import EvalType

class AppUsageRule(EvalType):
    def evaluate(self, context) -> int:
        app_name = self.rule["target"]
        interval = self.rule["points"]["interval"]
        point_value = self.rule["points"]["value"]
        max_points = self.rule.get("max_points")

        usage_minutes = context.get("app_usage", {}).get(app_name, 0)
        intervals = usage_minutes // interval
        total_points = intervals * point_value

        if max_points is not None:
            total_points = min(total_points, max_points)

        return total_points
