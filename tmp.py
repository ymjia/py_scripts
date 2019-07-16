import re

class Test():
    def __init__(self):
        self._text1 = []
        self._text2 = []

    def change_text(self, in_list):
        in_list.append("a")

    def run(self):
        self.change_text(self._text1)


t = Test()
t.run()
print(t._text1)
