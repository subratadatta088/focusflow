from rules.app_usage import AppUsageRule
from rules.url_whitelist import URLWhitelistRule

RULE_TYPE_MAP = {
    "app_usage": AppUsageRule,
    "url_whitelist": URLWhitelistRule,
    # add more types here
}

def evaluate_all_rules(role_rules, context):
    score = 0
    for rule_def in role_rules["rules"]:
        rule_type = rule_def["type"]
        rule_class = RULE_TYPE_MAP[rule_type]
        evaluator = rule_class(rule_def)
        score += evaluator.evaluate(context)
    return score
