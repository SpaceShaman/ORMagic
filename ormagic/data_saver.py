def save(self):
    return self._update() if self.id else self._insert()
