from yaml import safe_load
from pathlib import Path


class ConfigLoader:
    def __init__(self):
        self.cache = {}

    def load(self, filename: str):
        if filename in self.cache:
            return self.cache[filename]

        p = Path(filename)

        if not p.exists():
            self.cache[filename] = {}
        else:
            with p.open() as f:
                self.cache[filename] = safe_load(f)

        return self.cache[filename]