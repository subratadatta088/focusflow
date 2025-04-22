CACHE_FILE = 'cache.json'

CACHE_INTERVAL = 3

CACHE_FLUSH_INTERVAL = 60

DB_FLUSH_INTERVAL = 120

ACTIVITY_TIMEOUT = 30

IMPORTANT_APPS = [
    "code",                 # Visual Studio Code
    "pycharm",
    "chrome.exe",        
    "sublime_text",
    "intellij idea",
    "terminal",
    "iterm2",
    "cmd.exe",
    "powershell",
    "chrome",
    "google chrome",
    "firefox",
    "brave",
    "edge",
    "postman",
    "docker",
    "docker desktop",
    "gitkraken",
    "github desktop",
    "notion",
    "slack",
    "zoom",
    "teams",
    "msteams",
    "discord",
    "trello",
    "jira",
    "obsidian"
]

THRESHOLD_ACTIVATION = 10        # seconds to activate suspicious session
THRESHOLD_SUSPICIOUS_TIME = 60  # seconds after which it's considered fake activity
PATTERN_WINDOW = 15             # how many entries to store
THRESHOLD_LONG_PRESS = 60       # seconds after which it's considered fake activity