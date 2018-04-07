"""
This file contains some improvements over standard QT5 UI elements.
"""
from PyQt5 import QtWidgets, QtCore


class BetterLineEdit(QtWidgets.QLineEdit):
    """
    QLineEdit extension: added mouse double click.
    I need this to open file browser by double click.
    """
    dclicked = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        QtWidgets.QLineEdit.__init__(self, *args, **kwargs)

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        """ typical way to add event handler """
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            self.dclicked.emit()
        return False


class BetterPlainTextEdit(QtWidgets.QPlainTextEdit):
    """
    Overloaded QPlainTextEdit to track focus out.
    Needed to implement autosaving of user answer.
    """
    focus_lost = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        QtWidgets.QPlainTextEdit.__init__(self, *args, **kwargs)

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        """ typical way to add event handler """
        if event.type() == QtCore.QEvent.FocusOut:
            self.focus_lost.emit()
        return False
