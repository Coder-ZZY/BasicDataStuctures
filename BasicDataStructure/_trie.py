class Trie:
    def __init__(self):
        self.data = {}
        self.is_word = False

    def insert(self, word: str) -> None:
        if not word:
            return
        current = self
        for i, char in enumerate(word):
            if not char in current.data.keys():
                current.data[char] = Trie()
            current = current.data[char]
        current.is_word = True

    def search(self, word: str) -> bool:
        if not word:
            return False
        current = self
        for i, char in enumerate(word):
            if not char in current.data.keys():
                return False
            current = current.data[char]
        return current.is_word

    def startsWith(self, prefix: str) -> bool:
        if not prefix:
            return False
        current = self
        for char in prefix:
            if not char in current.data.keys():
                return False
            current = current.data[char]
        return True
