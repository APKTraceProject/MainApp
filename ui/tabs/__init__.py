from .dashboard import build_dashboard, update_dashboard_cards
from .chat import build_chat_page, add_chat_bubble
from .settings import build_settings_page, browse_path, save_settings
from .manifest import build_manifest_page, update_manifest_page
from .placeholder import build_placeholder_page
from .permissions_tab import PermissionsTab

__all__ = [
    "build_dashboard",
    "update_dashboard_cards",
    "build_chat_page",
    "add_chat_bubble",
    "build_settings_page",
    "browse_path",
    "save_settings",
    "build_manifest_page",
    "update_manifest_page",
    "build_placeholder_page",
]