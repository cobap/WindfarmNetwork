"""."""

class Protocol():

    def __init__(self, length, type, enconding):
        header = {}

        header['length'] = length
        header['type'] = type
        header['enconding'] = enconding

        self.header = header

    def add_content(self, content):
        self.content = content

    def get_content(self):
        return self.content
