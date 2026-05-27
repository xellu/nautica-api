import tomlkit

class OptionBuilder:
    def __init__(self):
        self._doc = tomlkit.document()

    def add(self, key: str, default, comment: str | None = None):
        item = tomlkit.item(default)
        if comment:
            item.comment(comment)

        parts = key.split(".")
        if len(parts) == 1:
            self._doc.add(key, item)
        else:
            context = self._doc
            for part in parts[:-1]:
                if part not in context:
                    context.add(part, tomlkit.table())
                context = context[part]
            context.add(parts[-1], item)

        return self

    def build(self):
        return self._doc
