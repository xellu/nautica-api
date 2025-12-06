from .levels import LogLevel

class TableUtil:
    def __init__(self, logger):
        self.logger = logger
        self._rows: list[list[str]] = []
        self._labels: list[list[str]] = []
        
    def labels(self, values: list[str]):
        self._labels = values
    
    def row(self, values: list[str]):
        self._rows.append(values)
        
        return self
        
    def display(self, level = LogLevel.INFO):
        all_rows = [self._labels] + self._rows if self._labels else self._rows
        
        if not all_rows:
            self.logger.log("(empty table)", level)
            return
        
        col_widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(all_rows[0]))]

        def format_row(row):
            return "| " + " | ".join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row)) + " |"
        
        # Build table
        lines = []
        lines.append("┌-" + "-┬-".join("-" * w for w in col_widths) + "-┐")
        if self._labels:
            lines.append(format_row(self._labels))
            lines.append("├-" + "-+-".join("-" * w for w in col_widths) + "-┤")
        for r in self._rows:
            lines.append(format_row(r))
        
        lines.append("└-" + "-┴-".join("-" * w for w in col_widths) + "-┘")

        
        # Print via logger
        for line in lines:
            self.logger.log(line, level)