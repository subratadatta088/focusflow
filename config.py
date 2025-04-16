SCORING_RULES = {
    "developer": {
        "rules": [
            {
                "name": "vs_code_usage",
                "type": "app_usage",
                "target": "VS Code",
                "points": {"value": 10, "interval": 30},
                "max_points": 40
            },
            {
                "name": "dev_browser_usage",
                "type": "url_whitelist",
                "target": ["localhost", "github.com"],
                "points": {"value": 5, "interval": 30}
            }
        ]
    }
}
