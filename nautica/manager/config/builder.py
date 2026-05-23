import tomlkit

class OptionBuilder:
    def __init__(self):
        self._doc = tomlkit.document()

    def add(self, key: str, default, comment: str | None = None):
        item = tomlkit.item(default)
        if comment:
            item.comment(comment)
        self._doc.add(key, item)
        return self

    def build(self):
        return self._doc
