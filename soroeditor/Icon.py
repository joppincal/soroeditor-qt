from darkdetect import isDark
from PySide6.QtGui import QPixmap


class Icon:
    def __init__(self):
        super().__init__()
        if isDark():
            color = "white"
        else:
            color = "black"
        directory = "soroeditor/src/icon/"
        self.Icon = QPixmap(f"{directory}/Icon.svg")
        self.Balance = QPixmap(f"{directory}/{color}/Balance.svg")
        self.Bookmark = QPixmap(f"{directory}/{color}/Bookmark.svg")
        self.Close = QPixmap(f"{directory}/{color}/Close.svg")
        self.Copy = QPixmap(f"{directory}/{color}/Copy.svg")
        self.Cut = QPixmap(f"{directory}/{color}/Cut.svg")
        self.Export = QPixmap(f"{directory}/{color}/Export.svg")
        self.FullScreen = QPixmap(f"{directory}/{color}/FullScreen.svg")
        self.Help = QPixmap(f"{directory}/{color}/Help.svg")
        self.History = QPixmap(f"{directory}/{color}/History.svg")
        self.Import = QPixmap(f"{directory}/{color}/Import.svg")
        self.Info = QPixmap(f"{directory}/{color}/Info.svg")
        self.NewFile = QPixmap(f"{directory}/{color}/NewFile.svg")
        self.OpenFile = QPixmap(f"{directory}/{color}/OpenFile.svg")
        self.Paste = QPixmap(f"{directory}/{color}/Paste.svg")
        self.Play = QPixmap(f"{directory}/{color}/Play.svg")
        self.ProjectSetting = QPixmap(
            f"{directory}/{color}/ProjectSetting.svg"
        )
        self.Refresh = QPixmap(f"{directory}/{color}/Refresh.svg")
        self.Redo = QPixmap(f"{directory}/{color}/Redo.svg")
        self.Replace = QPixmap(f"{directory}/{color}/Replace.svg")
        self.SaveFile = QPixmap(f"{directory}/{color}/SaveFile.svg")
        self.SaveFileAs = QPixmap(f"{directory}/{color}/SaveFileAs.svg")
        self.Search = QPixmap(f"{directory}/{color}/Search.svg")
        self.Select = QPixmap(f"{directory}/{color}/Select.svg")
        self.SelectAll = QPixmap(f"{directory}/{color}/SelectAll.svg")
        self.Setting = QPixmap(f"{directory}/{color}/Setting.svg")
        self.Template = QPixmap(f"{directory}/{color}/Template.svg")
        self.Undo = QPixmap(f"{directory}/{color}/Undo.svg")
