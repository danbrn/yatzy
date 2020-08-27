#!/usr/bin/env python3

from collections import Counter
import random


class AlreadyScored(Exception):
    pass


class Combination:
    def __init__(self, name, calculation):
        self.name = name
        self.calculation = calculation
        self.locked_score = None

    def score(self):
        return self.score_or_none() or 0

    def score_or_none(self):
        return self.locked_score

    def score_string(self):
        score = self.score_or_none()
        if score is None:
            return ""
        elif score == 0:
            return "---"
        else:
            return str(score)

    def calculate_score(self, dice):
        if self.locked_score is not None:
            return self.locked_score
        return self.calculation(dice)

    def set_score(self, dice):
        if self.locked_score is not None:
            raise AlreadyScored
        self.locked_score = self.calculation(dice)


class Bonus(Combination):
    def __init__(self, name, scoreboard):
        self.name = name
        self.scoreboard = scoreboard
        self.locked_score = None

    def calculate_score(self, ignored=None):
        if sum(map(lambda x: x.score(), self.scoreboard.combinations[:6])) >= 63:
            return 50
        return 0

    def set_score(self, ignored=None):
        if self.locked_score is not None:
            raise AlreadyScored
        self.locked_score = self.calculate_score()


def calculate_n(n):
    def calc(dice):
        return dice.count(n) * n

    return calc


def calculate_n_of_a_kind(n):
    def calc(dice):
        counts = Counter(dice)
        for die in sorted(counts.keys(), reverse=True):
            if counts[die] >= n:
                return die * n
        return 0

    return calc


def calculate_straight_to_n(n):
    def calc(dice):
        if sorted(dice) == list(range(n - 4, n + 1)):
            return sum(dice)
        return 0

    return calc


def calculate_two_pair(dice):
    counts = Counter(dice)
    score = 0
    for die in sorted(counts.keys(), reverse=True):
        if counts[die] >= 2:
            if score > 0:
                return score + 2 * die
            else:
                score = 2 * die
    return 0


def calculate_full_house(dice):
    counts = Counter(dice)
    if len(counts.keys()) != 2 or 2 not in counts.values():
        return 0
    return sum(dice)


def calculate_yatzy(dice):
    if calculate_n_of_a_kind(5)(dice) > 0:
        return 50
    return 0


class Scoreboard:
    def __init__(self):
        self.combinations = []
        self.combinations.append(Combination("Ettor", calculate_n(1)))
        self.combinations.append(Combination("Tvåor", calculate_n(2)))
        self.combinations.append(Combination("Treor", calculate_n(3)))
        self.combinations.append(Combination("Fyror", calculate_n(4)))
        self.combinations.append(Combination("Femmor", calculate_n(5)))
        self.combinations.append(Combination("Sexor", calculate_n(6)))
        self.combinations.append(Bonus("Bonus", self))
        self.bonus = self.combinations[-1]
        self.combinations.append(Combination("Par", calculate_n_of_a_kind(2)))
        self.combinations.append(Combination("Två par", calculate_two_pair))
        self.combinations.append(Combination("Triss", calculate_n_of_a_kind(3)))
        self.combinations.append(Combination("Liten stege", calculate_straight_to_n(5)))
        self.combinations.append(Combination("Stor stege", calculate_straight_to_n(6)))
        self.combinations.append(Combination("Kåk", calculate_full_house))
        self.combinations.append(Combination("Fyrtal", calculate_n_of_a_kind(4)))
        self.combinations.append(Combination("Chans", sum))
        self.combinations.append(Combination("Yatzy", calculate_yatzy))

    def score(self):
        return sum(map(lambda x: x.score(), self.combinations))

    def unscored(self):
        return list(
            filter(
                lambda x: x.score_or_none() is None and x != self.bonus,
                self.combinations,
            )
        )

    def set_bonus(self):
        if self.bonus.locked_score is not None or (
            sum(map(lambda x: x.score(), self.combinations[:6])) < 63
            and any(map(lambda x: x.score_or_none() is None, self.combinations[:6]))
        ):
            return
        self.bonus.set_score()


class Player:
    def __init__(self, name):
        self.name = name
        self.scoreboard = Scoreboard()


def input_number(prompt, low=None, high=None):
    number = None
    while number is None:
        number_str = input(prompt)
        try:
            number = int(number_str)
        except ValueError:
            print("Du måste ange ett heltal.")
            continue
        if low is None and high is None:
            return number
        if low is not None and high is not None:
            if number < low or number > high:
                print("Du måste ange ett tal mellan {} och {}.".format(low, high))
                number = None
                continue
            return number
        if low is not None and number < low:
            print("Du måste ange ett tal lika med eller över {}.".format(low))
            number = None
            continue
        if high is not None and number > high:
            print("Du måste ange ett tal lika med eller under {}.".format(high))
            number = None
            continue
    return number


def input_string(prompt, default=None, minimum_length=0, maximum_length=None):
    string = None
    while string is None:
        string = input(prompt)
        if default is not None and string == "":
            return default
        string_length = len(string)
        if string_length < minimum_length:
            print("Minsta tillåtna längd: {}".format(minimum_length))
            string = None
            continue
        if maximum_length is not None and string_length > maximum_length:
            print("Största tillåtna längd: {}".format(maximum_length))
            string = None
            continue
    return string


def input_number_of_players():
    return input_number("Antal spelare: ", low=1, high=6)


def input_player_name(player_number):
    return input_string(
        "Namn för spelare {}: ".format(player_number),
        default="Spelare {}".format(player_number),
        minimum_length=3,
        maximum_length=12,
    )


def roll_dice(number_of_dice=5):
    dice = []
    for i in range(0, number_of_dice):
        dice.append(random.randint(1, 6))
    return dice


def reroll_unsaved(saved_dice):
    return saved_dice + roll_dice(5 - len(dice))


def request_action(roll, dice):
    command = None
    while command is None:
        command = input_string(
            "\nSlag {}, spara tärningar med a-e, q om du är nöjd: ".format(roll + 2)
        ).lower()
        if command == "":
            return []
        if command == "q":
            return dice
        return list(
            map(
                lambda x: dice[ord(x) - ord("a")],
                filter(lambda x: x >= "a" and x <= "e", list(command)),
            )
        )


def print_scores(players):
    print("             ", end="")
    for player in players:
        print("{0: >12} ".format(player.name), end="")
    print()
    for i in range(len(players[0].scoreboard.combinations)):
        print("{0: >12} ".format(players[0].scoreboard.combinations[i].name), end="")
        for player in players:
            print(
                "{0: >12} ".format(player.scoreboard.combinations[i].score_string()),
                end="",
            )
        print()
        if player.scoreboard.combinations[i] == player.scoreboard.bonus:
            print()
    print("\n       Summa ", end="")
    for player in players:
        print("{0: >12} ".format(player.scoreboard.score()), end="")
    print("\n")


dice_graphics_lines = [
    ["     ", "  *  ", "     "],
    ["*    ", "     ", "    *"],
    ["    *", "  *  ", "*    "],
    ["*   *", "     ", "*   *"],
    ["*   *", "  *  ", "*   *"],
    ["*   *", "*   *", "*   *"],
]


def print_dice_edges(dice):
    for die in dice:
        print("+-------+  ", end="")
    print()


def print_dice_labels(dice):
    for dice_num in range(len(dice)):
        print("    {}      ".format(chr(ord("A") + dice_num)), end="")
    print()


def print_dice_line(dice, line):
    # +-------+
    # | .   . |
    # | . . . |
    # | .   . |
    # +-------+
    #     A
    if line == 0 or line == 4:
        print_dice_edges(dice)
    else:
        for dice_num in range(len(dice)):
            print(
                "| {} |  ".format(dice_graphics_lines[dice[dice_num] - 1][line - 1]),
                end="",
            )
        print()


def print_dice(dice):
    for line in range(5):
        print_dice_line(dice, line)


print("Välkommen till Yatzy!")

num_players = input_number_of_players()

players = []
for player_num in range(1, num_players + 1):
    players.append(Player(input_player_name(player_num)))


while players[0].scoreboard.unscored():
    for player in players:
        print_scores(players)
        print("{}:".format(player.name))
        dice = roll_dice(5)
        for roll in range(2):
            print_dice(dice)
            print_dice_labels(dice)
            dice = request_action(roll, dice)
            if len(dice) == 5:
                print_dice(dice)
                break
            dice = reroll_unsaved(dice)
        i = 0
        unscored = player.scoreboard.unscored()
        print()
        for c in unscored:
            i = i + 1
            print("{0: >2}: {1} {2}".format(i, c.name, c.calculate_score(dice)))
        print_dice(dice)
        unscored[
            input_number("Välj kombination (1-{}): ".format(i), 1, i) - 1
        ].set_score(dice)
        print()
        player.scoreboard.set_bonus()

print_scores(players)
