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
        return self.locked_score or 0

    def score_or_none(self):
        return self.locked_score

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

    def score(self):
        return self.calculate_score()

    def score_or_none(self):
        return self.score()

    def calculate_score(self, ignored=None):
        if sum(map(lambda x: x.score(), self.scoreboard.combinations[:6])) >= 63:
            return 50
        return 0

    def set_score(self, ignored=None):
        pass


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
        counts = Counter(dice)
        if len(counts.keys()) != 5 or max(counts.keys()) != n:
            return 0
        return sum(dice)

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


class Scoreboard:
    combinations = []

    def __init__(self):
        self.combinations.append(Combination("Ettor", calculate_n(1)))
        self.combinations.append(Combination("Tvåor", calculate_n(2)))
        self.combinations.append(Combination("Treor", calculate_n(3)))
        self.combinations.append(Combination("Fyror", calculate_n(4)))
        self.combinations.append(Combination("Femmor", calculate_n(5)))
        self.combinations.append(Combination("Sexor", calculate_n(6)))
        self.combinations.append(Bonus("Bonus", self))
        self.combinations.append(Combination("Par", calculate_n_of_a_kind(2)))
        self.combinations.append(Combination("Två par", calculate_two_pair))
        self.combinations.append(Combination("Triss", calculate_n_of_a_kind(3)))
        self.combinations.append(Combination("Liten stege", calculate_straight_to_n(5)))
        self.combinations.append(Combination("Stor stege", calculate_straight_to_n(6)))
        self.combinations.append(Combination("Kåk", calculate_full_house))
        self.combinations.append(Combination("Fyrtal", calculate_n_of_a_kind(4)))
        self.combinations.append(Combination("Chans", sum))
        self.combinations.append(Combination("Yatzy", calculate_n_of_a_kind(5)))

    def score(self):
        return sum(map(lambda x: x.score(), self.combinations))

    def unscored(self):
        return filter(lambda x: x.score_or_none() is None, self.combinations)


class Player:
    scoreboard = Scoreboard()

    def __init__(self, name):
        self.name = name


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
        if string_length > maximum_length:
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


print("Välkommen till Yatzy!")

num_players = input_number_of_players()

players = []
for player_num in range(1, num_players + 1):
    players.append(Player(input_player_name(player_num)))

for player in players:
    print("{}:".format(player.name))
    dice = roll_dice()
    i = 0
    unscored = player.scoreboard.unscored()
    for c in unscored:
        i = i + 1
        print("{0: >2}: {1} ({2})".format(i, c.name, c.calculate_score(dice)))
