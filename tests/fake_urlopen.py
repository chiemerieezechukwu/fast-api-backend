import json


class FakeUrlOpen:
    def __init__(self, return_value):
        self.return_value = return_value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read(self):
        return json.dumps(self.return_value).encode()
