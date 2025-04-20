from .app_usage.tracker import AppUsageTracker
from .app_activity.tracker import ActivityTracker
from .base import BaseTracker

TRACKER_SERVICES: BaseTracker = [AppUsageTracker, ActivityTracker]
