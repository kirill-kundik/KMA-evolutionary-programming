import typing

import numpy as np

import models


class Population:
    def __init__(self, individuals: typing.List[models.Individual]):
        self._individuals: typing.List[models.Individual] = sorted(
            individuals, key=lambda x: x.fitness, reverse=True
        )
        self._score: typing.Union[float, None] = None
        self._avg_score: typing.Union[float, None] = None
        self._std_score: typing.Union[float, None] = None
        self._fitness_arr: typing.Union[typing.List[float], None] = None

    @property
    def individuals(self) -> typing.List[models.Individual]:
        return self._individuals

    @property
    def score(self) -> float:
        if self._score is None:
            self._score = sum(self.fitness_arr)

        return self._score

    @property
    def avg_score(self) -> float:
        if self._avg_score is None:
            self._avg_score = np.mean(self.fitness_arr)

        return self._avg_score

    @property
    def std_score(self) -> float:
        if self._std_score is None:
            self._std_score = np.std(self.fitness_arr)

        return self._std_score

    @property
    def fitness_arr(self) -> typing.List[float]:
        if self._fitness_arr is None:
            self._fitness_arr = [individual.fitness for individual in self._individuals]

        return self._fitness_arr

    def get_fittest(self, n: int) -> typing.List[models.Individual]:
        return self._individuals[:n]

    def count(self, individual: models.Individual) -> int:
        counter = 0

        for i in self._individuals:
            if i == individual:
                counter += 1

        return counter

    def __repr__(self):
        return f"Population(individuals={len(self._individuals)}, total_score={self.score})"

    def __contains__(self, item) -> bool:
        return item in self._individuals

    def __eq__(self, other) -> bool:
        return self._individuals == other.individuals
