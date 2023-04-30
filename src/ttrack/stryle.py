_decorations = {
    "header": '\033[95m',
    "blue": '\033[94m',
    "cyan": '\033[96m',
    "green": '\033[92m',
    "yellow": '\033[93m',
    "red": '\033[91m',
    "warning": '\033[93m',
    "fail": '\033[91m',
    "off": '\033[0m',
    "bold": '\033[1m',
    "underline": '\033[4m',
}


class _StringStyle(str):
    header: str
    blue: str
    cyan: str
    green: str
    yellow: str
    red: str
    warning: str
    fail: str
    off: str
    bold: str
    underline: str

    def __getattribute__(self, decoration: str = _decorations["off"]):
        if decoration in _decorations:
            return _StringStyle(self.decorations + _decorations[decoration])
        return self

    def __matmul__(self, other):
        return self.decorations + str(other) + _decorations["off"]

    def __rmatmul__(self, other):
        return self.decorations + str(other) + _decorations["off"]

    def __str__(self):
        return self.decorations


Stryle = _StringStyle()
