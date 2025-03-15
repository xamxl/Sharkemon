from card import Card

class CardLibrary:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_card(self, name):
        for c in self.cards:
            if c.name == name:
                return c
        return None