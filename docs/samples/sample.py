import random
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class Kevin:
    name: str
    favorite_chili: str
    desk_location: str
    famous_quote: str

class KevinSecretSanta:
    def __init__(self):
        self.kevins: List[Kevin] = [
            Kevin("Kevin Malone", "Famous Chili", "Accounting Corner", "Why waste time say lot word when few word do trick"),
            Kevin("Kevin McCallister", "Microwave Mac & Chili", "Home Alone", "This is my house, I have to defend it"),
            Kevin("Kevin Hart", "Comedy Chili", "Stage Left", "Everybody wants to be famous, but nobody wants to do the work"),
            Kevin("Kevin Bacon", "Six Degrees of Chili", "Hollywood", "Everything is connected by six degrees of separation"),
            Kevin("Kevin Durant", "Championship Chili", "Basketball Court", "Hard work beats talent when talent fails to work hard"),
            Kevin("Kevin James", "Mall Cop Chili", "Segway Station", "Safety never takes a holiday"),
        ]
        self.assignments: Dict[Kevin, Kevin] = {}

    def assign_secret_santas(self) -> None:
        recipients = self.kevins.copy()
        for giver in self.kevins:
            while True:
                recipient = random.choice(recipients)
                if recipient != giver:
                    self.assignments[giver] = recipient
                    recipients.remove(recipient)
                    break

    def print_assignments(self) -> None:
        print("\n🎅 KEVIN-THEMED SECRET SANTA ASSIGNMENTS 🎅")
        print("=" * 50)
        for giver, recipient in self.assignments.items():
            print(f"\n{giver.name} is getting a gift for {recipient.name}")
            print(f"Recipient's favorite chili: {recipient.favorite_chili}")
            print(f"Find them at: {recipient.desk_location}")
            print(f"Famous quote: '{recipient.famous_quote}'")

    def spill_chili(self) -> str:
        return """
        ⠀⠀⠀⠀⠀⠀⠀🌶️ Oh no! The chili! 🌶️
        ⠀⠀⠀⠀⠀⠀⠀   ___________
        ⠀⠀⠀⠀⠀⠀⠀  /           \\
        ⠀⠀⠀⠀⠀⠀⠀ |  * splat *  |
        ⠀⠀⠀⠀⠀⠀⠀  \\___________ /
        """

if __name__ == "__main__":
    santa = KevinSecretSanta()
    santa.assign_secret_santas()
    santa.print_assignments()
    print(santa.spill_chili())
    print("\nThe trick is to undercook the onions...")

