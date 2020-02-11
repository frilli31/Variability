# -*- coding: utf-8 -*-
"""Variability

This module defines three different functions to compute the variability of an
EventLog (pm4py.objects.log.EventLog)
"""
from pm4py.objects.log import log as lg
from itertools import combinations
from collections import Counter
import editdistance


def compute_variant_variability(log: lg.EventLog) -> int:
    """Compute the number of variants present in the event log

    Args:
        log (lg.EventLog): The log to examine

    Returns:
        int: The number of variants present in the event log
    """
    # For each case of the log we construct a tuple with the names of events.
    # Then we collect all of them in a set to remove duplicates.
    # Eventually we compute the length of the set.
    return len(set(tuple(event["concept:name"] for event in case) for case in log))


def compute_edit_distance_variability(log: lg.EventLog) -> float:
    """Compute the average edit distance (Levenshtein distance) between each
    pairs of traces.

    This function uses function `eval` of module 'editdistance' because it's
    implemented in C++ and it is faster than the corresponding implementation
    in python.

    Args:
        log (EventLog): The log to examine

    Returns:
        float: the average edit distance between each pairs of traces
    """
    # Create a dictionary which contains variants as keys and its number of
    # occurrences as values
    variants_and_counts = Counter(
        tuple(event["concept:name"] for event in case) for case in log
    )
    size_of_log = len(log)

    # For each pair of distinct variants (obtained by 'combinations') we
    # compute the edit distance and we multiply it for number of
    # occurrences of the variants.
    # In the end we sum all of them.
    sum_of_distances = sum(
        num_of_items_1 * num_of_items_2 * editdistance.eval(variant1, variant2)
        for (variant1, num_of_items_1), (variant2, num_of_items_2)
            in combinations(variants_and_counts.items(), 2)
    )

    # We multiply the sum of distances by 2 because to add the sum of distances
    # of each inverted pairs of variants.
    # In the end we divide it by the number of possible combination of pair
    # of traces
    return float(sum_of_distances * 2) / (size_of_log * (size_of_log - 1))


def compute_my_variability(log: lg.EventLog) -> float:
    """Compute the average of normalized edit distances (Levenshtein distance)
    between each pairs of traces.

    This function uses function `eval` of module 'editdistance' because it's
    implemented in C++ and it is faster than the corresponding implementation
    in python.

    Args:
        log (EventLog): The log to examine

    Returns:
        float: a number between 0 and 1 included. The higher the number the
            more similar the traces are
            - 0 : if all traces has nothing in common
            - 1 : all traces belongs to the same variant (are equals)
    """
    # Create a dictionary which contains variants as keys and its number of
    # occurrences as values
    variants_and_counts = Counter(
        tuple(event["concept:name"] for event in case) for case in log
    )
    size_of_log = len(log)

    # For each pair of distinct variants (obtained by 'combinations') we
    # compute the average edit distance normalized (divided by longest trace)
    # and we multiply it for number of occurrences of the variants.
    # In the end we sum all of them.
    sum_of_distances = sum(
        float(num_of_items_1 * num_of_items_2 * editdistance.eval(variant1, variant2))
        / max(len(variant1), len(variant2))
        for (variant1, num_of_items_1), (variant2, num_of_items_2)
            in combinations(variants_and_counts.items(), 2)
    )

    # We multiply the sum of distances by 2 because to add the sum of distances
    # of each inverted pairs of variants
    # In the end we divide it by the number of possible combination of pair
    # of traces
    return 1 - (sum_of_distances * 2 / (size_of_log * (size_of_log - 1)))
