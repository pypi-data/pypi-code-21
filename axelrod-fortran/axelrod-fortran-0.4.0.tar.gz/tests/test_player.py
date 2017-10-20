from axelrod_fortran import Player, characteristics, all_strategies
from axelrod import (Alternator, Cooperator, Defector,
                     Match, Game, basic_strategies, seed)
from axelrod.action import Action
from ctypes import c_int, c_float, POINTER, CDLL

import itertools
import pytest

C, D = Action.C, Action.D


def test_init():
    for strategy in all_strategies:
        player = Player(strategy)
        is_stochastic = characteristics[strategy]['stochastic'] in (True, None)
        assert player.classifier['stochastic'] == is_stochastic
        assert player.original_name == strategy
        assert player.original_function.argtypes == (
            POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int),
            POINTER(c_float))
        assert player.original_function.restype == c_int
        with pytest.raises(ValueError):
            player = Player('test')
        assert "libstrategies.so" == player.shared_library_name
        assert type(player.shared_library) is CDLL
        assert "libstrategies.so" in str(player.shared_library)

def test_init_with_shared():
    player = Player("k42r", shared_library_name="libstrategies.so")
    assert "libstrategies.so" == player.shared_library_name
    assert type(player.shared_library) is CDLL
    assert "libstrategies.so" in str(player.shared_library)


def test_matches():
    for strategy in all_strategies:
        for opponent in (Alternator, Cooperator, Defector):
            players = (Player(strategy), opponent())
            match = Match(players, turns=200)
            assert all(
                action in (C, D) for interaction in match.play()
                for action in interaction)


def test_noisy_matches():
    for strategy in all_strategies:
        for opponent in (Alternator, Cooperator, Defector):
            players = (Player(strategy), opponent())
            match = Match(players, turns=200, noise=0.5)
            assert all(
                action in (C, D) for interaction in match.play()
                for action in interaction)


def test_probend_matches():
    for strategy in all_strategies:
        for opponent in (Alternator, Cooperator, Defector):
            players = (Player(strategy), opponent())
            match = Match(players, prob_end=0.5, noise=0.5)
            assert all(
                action in (C, D) for interaction in match.play()
                for action in interaction)


def test_matches_with_different_game():
    for strategy in all_strategies:
        for opponent in (Alternator, Cooperator, Defector):
            game = Game(r=4, s=0, p=2, t=6)
            players = (Player(strategy), opponent())
            match = Match(players, turns=200, game=game)
            assert all(
                action in (C, D) for interaction in match.play()
                for action in interaction)


def test_original_strategy():
    """
    Test original strategy against all possible first 5 moves of a Match
    """
    actions_to_scores = {(0, 0): (3, 3), (0, 1): (0, 5),
                         (1, 0): (5, 0), (1, 1): (1, 1)}
    for strategy in all_strategies:
        for opponent_sequence in itertools.product((0, 1), repeat=5):

            player = Player(strategy)

            # Initial set up for empty history
            my_score, their_score = 0, 0
            move_number = 1
            their_previous_action, my_action = 0, 0

            for action in opponent_sequence:
                my_action = player.original_strategy(
                    their_last_move=their_previous_action,
                    move_number=move_number,
                    my_score=my_score,
                    their_score=their_score,
                    random_value=0,
                    my_last_move=my_action)

                assert my_action in [0, 1]

                scores = actions_to_scores[my_action, action]
                their_previous_action = action
                my_score += scores[0]
                their_score += scores[1]

def test_deterministic_strategies():
    """
    Test that the strategies classified as deterministic indeed act
    deterministically.
    """
    for strategy in all_strategies:
        player = Player(strategy)
        if player.classifier["stochastic"] is False:
            for opponent in basic_strategies:
                match = Match((player, opponent()))
                interactions = match.play()
                for _ in range(2):  # Repeat 3 matches
                    assert interactions == match.play(), player


def test_implemented_strategies():
    """
    Test that the deterministic strategies that are implemented in Axelrod
    give the same outcomes.
    """
    for strategy, dictionary in characteristics.items():
        axelrod_class = dictionary["axelrod-python_class"]
        player = Player(strategy)
        if (axelrod_class is not None and
            player.classifier["stochastic"] is False):
            axl_player = axelrod_class()
            for opponent_strategy in basic_strategies:
                opponent = opponent_strategy()
                match = Match((player, opponent))
                interactions = match.play()
                axl_match = Match((axl_player, opponent))
                assert interactions == axl_match.play(), (player, opponent)

def test_champion_v_alternator():
    """
    Specific regression test for a bug.
    """
    player = Player("k61r")
    opponent = Alternator()

    match = Match((player, opponent))

    seed(0)
    interactions = match.play()
    assert interactions[25:30] == [(C, D), (C, C), (C, D), (D, C), (C, D)]

    seed(0)
    assert interactions == match.play()

def test_warning_for_self_interaction(recwarn):
    """
    Test that a warning is given for a self interaction.
    """
    player = Player("k42r")
    opponent = Player("k42r")

    match = Match((player, opponent))

    interactions = match.play()
    assert len(recwarn) == 1

def test_no_warning_for_normal_interaction(recwarn):
    """
    Test that a warning is not given for a normal interaction
    """
    player = Player("k42r")
    opponent = Alternator()
    for players in [(Player("k42r"), Alternator()),
                    (Player("k42r"), Player("k41r"))]:

        match = Match(players)

        interactions = match.play()
        assert len(recwarn) == 0
