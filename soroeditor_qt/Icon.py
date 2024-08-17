from pathlib import Path

from darkdetect import isDark
from PySide6.QtGui import QPixmap


class Icon:
    def __init__(self):
        super().__init__()
        self.theme = "light" if not isDark() else "dark"
        self.directory = Path(__file__).parent / "src" / "icon"

        self.AppIcon = self._loadIcon("AppIcon.svg")
        self._loadThemedIcons()

    def _loadIcon(self, filename):
        return QPixmap(self.directory / filename)

    def _loadThemedIcon(self, name):
        return self._loadIcon(self.directory / self.theme / f"{name}.svg")

    def _loadThemedIcons(self):
        themedIcons = [
            "Balance",
            "Bookmark",
            "Close",
            "Copy",
            "Cut",
            "Export",
            "FullScreen",
            "Help",
            "History",
            "Import",
            "Info",
            "NewFile",
            "OpenFile",
            "Paste",
            "Play",
            "ProjectSetting",
            "Refresh",
            "Redo",
            "Replace",
            "SaveFile",
            "SaveFileAs",
            "Search",
            "Select",
            "SelectAll",
            "Setting",
            "Template",
            "Undo",
        ]

        for iconName in themedIcons:
            setattr(self, iconName, self._loadThemedIcon(iconName))
