import json
import os
import random
from datetime import datetime, timedelta

class Card:
    def __init__(self, question, answer, interval=1, easiness=2.5, reps=0, last_review=None):
        self.question = question
        self.answer = answer
        self.interval = interval
        self.easiness = easiness
        self.reps = reps
        self.last_review = last_review or datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "question": self.question,
            "answer": self.answer,
            "interval": self.interval,
            "easiness": self.easiness,
            "reps": self.reps,
            "last_review": self.last_review
        }

    @staticmethod
    def from_dict(d):
        return Card(d["question"], d["answer"], d.get("interval",1), d.get("easiness",2.5), d.get("reps",0), d.get("last_review"))

class Deck:
    def __init__(self, filename="deck.json"):
        self.filename = filename
        self.cards = []
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                data = json.load(f)
                self.cards = [Card.from_dict(x) for x in data]
        else:
            self._save()

    def _save(self):
        with open(self.filename, "w") as f:
            json.dump([c.to_dict() for c in self.cards], f, indent=2)

    def add_card(self, question, answer):
        self.cards.append(Card(question, answer))
        self._save()

    def due_cards(self):
        today = datetime.now().date()
        due = []
        for c in self.cards:
            last = datetime.strptime(c.last_review, "%Y-%m-%d").date()
            if last + timedelta(days=c.interval) <= today:
                due.append(c)
        return due

    def review_card(self, card, quality):
        if quality < 3:
            card.reps = 0
            card.interval = 1
        else:
            card.reps += 1
            if card.reps == 1:
                card.interval = 1
            elif card.reps == 2:
                card.interval = 6
            else:
                card.interval = int(card.interval * card.easiness)
        card.easiness = max(1.3, card.easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        card.last_review = datetime.now().strftime("%Y-%m-%d")
        self._save()

def run_review_loop():
    deck = Deck()
    while True:
        print("\n1. Add card\n2. Review due cards\n3. Show deck stats\n4. Exit")
        cmd = input("Choose: ").strip()
        if cmd == "1":
            q = input("Question: ").strip()
            a = input("Answer: ").strip()
            deck.add_card(q, a)
            print("Added.")
        elif cmd == "2":
            due = deck.due_cards()
            if not due:
                print("No cards due. Well done.")
                continue
            random.shuffle(due)
            for c in due:
                print("\nQ:", c.question)
                _ = input("Press enter to show answer...")
                print("A:", c.answer)
                print("Rate yourself 0-5 (0 = complete blackout, 5 = perfect):")
                try:
                    q = int(input().strip())
                    if q < 0 or q > 5:
                        raise ValueError
                except:
                    print("Invalid rating, counted as 0.")
                    q = 0
                deck.review_card(c, q)
                print("Updated. Next interval:", c.interval, "days")
        elif cmd == "3":
            total = len(deck.cards)
            due = len(deck.due_cards())
            print(f"Cards: {total}, Due now: {due}")
        elif cmd == "4":
            print("Good luck learning!")
            break
        else:
            print("Try again.")

if __name__ == "__main__":
    run_review_loop()
