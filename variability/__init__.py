# -*- coding: utf-8 -*-
"""Variability

This module defines three different function to compute variability of a EventLog (pm4py.objects.log.EventLog)
"""
from pm4py.objects.log import log as lg
from itertools import combinations
from collections import Counter
import editdistance
from functools import reduce
from itertools import zip_longest


def compute_variant_variability(log: lg.EventLog) -> int:
    """Compute the number of variants present of the event log

    Args:
        log (EventLog): The log to examine

    Returns:
        int: The number of variants present of the event log
    """
    return len(set(tuple(event["concept:name"] for event in case) for case in log))


import numpy as np
from typing import Tuple


def damerau_leveshtein_distance(s: Tuple[str], t: Tuple[str]) -> int:
    """Compute the edit distance (Levenshtein distance) between two tuples of strings
        The complete explanation can be found here: https://en.wikipedia.org/wiki/Levenshtein_distance

        Args:
            s (Tuple[str]): the first
            t (Tuple[str]): the second argument to compare

        Returns:
            int: the edit distance between the tuples
        """
    n = len(s)
    mm = len(t)
    d = np.zeros((n + 1, mm + 1))

    for i in range(1, n + 1):
        d[i, 0] = i
    for j in range(1, mm + 1):
        d[0, j] = j
    for i in range(1, n + 1):
        substitution_cost = 0 if s[i - 1] == t[0] else 1
        d[i, 1] = min(d[i - 1, 1] + 1, d[i, 0] + 1, d[i - 1, 0] + substitution_cost)
    for j in range(2, mm + 1):
        substitution_cost = 0 if s[0] == t[j - 1] else 1
        d[1, j] = min(d[1, j - 1] + 1, d[0, j] + 1, d[0, j - 1] + substitution_cost)
    for i in range(2, n + 1):
        for j in range(2, mm + 1):
            substitution_cost = 0 if s[i - 1] == t[j - 1] else 1
            transposition_cost = (
                1 if s[i - 1] == t[j - 2] and s[i - 2] == t[j - 1] else 2
            )
            d[i, j] = min(
                d[i - 1, j] + 1,
                d[i, j - 1] + 1,
                d[i - 1, j - 1] + substitution_cost,
                d[i - 2, j - 2] + transposition_cost,
            )
    return d[n, mm]


def compute_edit_distance_variability(log: lg.EventLog) -> float:
    """Compute the average edit distance (Levenshtein distance) between each pairs of traces.

    We use the module 'editdistance' because it's implemented in C++ so It is too fast than the corresponding
    implementation in python

    Args:
        log (EventLog): The log to examine

    Returns:
        float: the average edit distance between each pairs of traces
    """
    variants_and_n_of_occurrences = Counter(
        tuple(event["concept:name"] for event in case) for case in log
    )
    size_of_log = len(log)

    sum_of_distances = sum(
        num_of_items_1 * num_of_items_2 * editdistance.eval(variant1, variant2)
        for (variant1, num_of_items_1), (variant2, num_of_items_2) in combinations(
            variants_and_n_of_occurrences.items(), 2
        )
    )

    return float(sum_of_distances * 2) / (size_of_log * (size_of_log - 1))


def lzw(trace):
    dictionary = set()
    result = ()
    w = ()

    for item in trace:
        if w + (item, ) in dictionary:
            w += (item, )
        else:
            dictionary.add(w + (item, ))
            if w is not ():
                result += (w, )
            w = (item, )
    result += (w, )
    return result


def zipped_lzw(first, second):
    dictionary = set()
    result_1 = ()
    result_2 = ()
    w_1 = ()
    w_2 = ()

    for item_1, item_2 in zip_longest(first, second):
        cond_1 = True
        cond_2 = True

        if item_1 and w_1 + (item_1,) in dictionary:
            w_1 += (item_1,)
            cond_1 = False
        if item_2 and w_2 + (item_2,) in dictionary:
            w_2 += (item_2,)
            cond_2 = False
        if item_1 and cond_1:
            dictionary.add(w_1 + (item_1,))
            if w_1 is not ():
                result_1 += (w_1,)
            w_1 = (item_1,)
        if item_2 and cond_2:
            dictionary.add(w_2 + (item_2,))
            if w_2 is not ():
                result_2 += (w_2,)
            w_2 = (item_2,)

    result_1 += (w_1,)
    result_2 += (w_2,)
    return result_1, result_2


def compute_my_variability(log: lg.EventLog):
    variants_with_repetitions = [
        tuple(event["concept:name"] for event in case) for case in log
    ]
    variants_and_n_of_occurrences = Counter(variants_with_repetitions)

    sum_of_distances = 0
    sum_of_length = 0
    for (variant1, num_of_items_1), (variant2, num_of_items_2) in combinations(
            variants_and_n_of_occurrences.items(), 2
    ):
        sum_of_distances += num_of_items_1 * num_of_items_2 * editdistance.eval(variant1, variant2)
        sum_of_length += num_of_items_1 * num_of_items_2 * max(len(variant1), len(variant2))

    sum_of_length += (
            sum(len(k) * v * (v - 1) for k, v in variants_and_n_of_occurrences.items()) / 2
    )
    return 1 - (float(sum_of_distances) / sum_of_length)


def compute_my_variability_lzw(log: lg.EventLog):
    """My edit distance

    We use the module 'editdistance' because it's implemented in C++ so It is too fast than the corresponding
    implementation in python

    The edit distance penalize too much if the length of the two cases if very different, but we can have
    cycle in our model and in this case i would like to penalize less the next iteration over a cycle respect
    to complete different traces.
    Applying LZW we penalize less if a trace do lots of iteration in a loop and another do few. But also we
    penalize the ratio if two traces do lots of iteration
    -> it smooths the cycle effect that is devastating using only LZW
    For example using file "L3.xes", that has a cycle inside, using LZW increase similarity ratio

    Example:
        ABCDBCDBCD and ABCDBCD are more similar than ABCDBCDBCD and ABCDBCDZZZ while the edit distance is the same

    Compress both cases using LZW (substitute sequence with tuple of elements, i don't case size but the repetition of
        same elements,
        so less penalization) an then compute the edit distance between the two obtained string
        return the minimum between DamerauLevenshtein of traces and LZW compressed traces

        why not compare LZWcode instead of tuple? It wold means repetitions of same pattern in the same position

    Args:
        log (EventLog): The log to examine

    Returns:
        float: a number between 0 and 1 that correspond to variability.
            0 means that maximum variability between traces, so they have nothing in common
            1 means that traces are all the same
    """
    variants_with_repetitions = [
        tuple(event["concept:name"] for event in case) for case in log
    ]
    variants_and_n_of_occurrences = Counter(variants_with_repetitions)
    variants_and_n_of_occurrences = dict((lzw(var), n) for var, n in variants_and_n_of_occurrences.items())

    sum_of_distances = 0
    sum_of_length = 0
    for (variant1, num_of_items_1), (variant2, num_of_items_2) in combinations(
            variants_and_n_of_occurrences.items(), 2
    ):
        sum_of_distances += num_of_items_1 * num_of_items_2 * editdistance.eval(variant1, variant2)
        sum_of_length += num_of_items_1 * num_of_items_2 * max(len(variant1), len(variant2))

    sum_of_length += (
            sum(len(k) * v * (v - 1) for k, v in variants_and_n_of_occurrences.items()) / 2
    )
    return 1 - (float(sum_of_distances) / sum_of_length)


def medium_length(log: lg.EventLog):
    variants_and_n_of_occurrences = Counter(
        tuple(event["concept:name"] for event in case) for case in log
    )
    size_of_log = len(log)
    return sum(len(v)*n for v, n in variants_and_n_of_occurrences.items()) / size_of_log


if __name__ == "__main__":
    # print(damerau_leveshtein_distance("ciao", "icao"))

    s1 = ('assumption laboratory', 'assumption laboratory', 'assumption laboratory', 'unconjugated bilirubin', 'bilirubin - total', 'glucose', 'urea', 'hemoglobin photoelectric', 'creatinine', 'alkaline phosphatase-kinetic-', 'sodium flame photometry', 'potassium potentiometrically', 'SGOT - Asat kinetic', 'SGPT - alat kinetic', 'Milk acid dehydrogenase LDH kinetic', 'ABO blood group and rhesus factor', 'rhesus factor d - Centrifuge method - email', 'leukocyte count electronic', 'platelet count - Electronic', 'gammaglutamyltranspeptidase', 'CEA - tumor marker using meia', 'calcium', 'albumin', 'red cell antibody screening', 'ca-125 using meia', 'differentiation leukocytes - manual', 'order rate', 'First outpatient consultation', 'administrative fee - the first pol', 'thorax', 'thorax', 'ct abdomen', 'ct abdomen', 'demurrage - all spec.beh.kinderg.-Reval.', 'assumption laboratory', 'assumption laboratory', 'assumption laboratory', 'urea', 'hemoglobin photoelectric', 'creatinine', 'sodium flame photometry', 'potassium potentiometrically', 'ABO blood group and rhesus factor', 'rhesus factor d - Centrifuge method - email', 'differential count automatically', 'leukocyte count electronic', 'platelet count - Electronic', 'red cell antibody screening', 'order rate', '190021 clinical admission A002', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', 'ovarian - ovarian redebulking CarCine', 'immuno-pathology', 'immuno-pathology', 'cytology - ascites -', 'histological examination - big resectiep', 'assumption laboratory', 'assumption laboratory', 'assumption laboratory', 'glucose', 'glucose', 'methemoglobin - sulphemoglobin each', 'hemoglobin photoelectric', 'hemoglobin photoelectric', 'bicarbonate', 'Co-hb kwn.', 'sodium flame photometry', 'sodium flame photometry', 'potassium potentiometrically', 'potassium potentiometrically', 'platelet count - Electronic', 'cefalinetijd - coagulation', 'Current ph - PCO2 - stand.bicarbonaat', 'crossmatch methods, three fully-', 'crossmatch methods, three fully-', 'lactic acid enzymatic', 'lactic acid enzymatic', 'calcium', 'calcium', 'O2 saturation', 'O2 saturation', 'prothrombin', 'order rate', 'order rate', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'filtered red cells', 'demurrage - all spec.beh.kinderg.-Reval.', 'assumption laboratory', 'assumption laboratory', 'urea', 'hemoglobin photoelectric', 'creatinine', 'sodium flame photometry', 'potassium potentiometrically', 'SGOT - Asat kinetic', 'SGPT - alat kinetic', 'leukocyte count electronic', 'platelet count - Electronic', 'gammaglutamyltranspeptidase', 'CRP c-reactive protein', 'order rate', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', 'assumption laboratory', 'assumption laboratory', 'hemoglobin photoelectric', 'creatinine', 'sodium flame photometry', 'potassium potentiometrically', 'order rate', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'telephone consultation')
    s2 = ('demurrage - all spec.beh.kinderg.-Reval.', 'assumption laboratory', 'assumption laboratory', 'assumption laboratory', 'unconjugated bilirubin', 'bilirubin - total', 'glucose', 'urea', 'hemoglobin photoelectric', 'creatinine', 'alkaline phosphatase-kinetic-', 'sodium flame photometry', 'potassium potentiometrically', 'SGOT - Asat kinetic', 'SGPT - alat kinetic', 'Milk acid dehydrogenase LDH kinetic', 'ABO blood group and rhesus factor', 'rhesus factor d - Centrifuge method - email', 'leukocyte count electronic', 'platelet count - Electronic', 'gammaglutamyltranspeptidase', 'CEA - tumor marker using meia', 'squamous cell carcinoma using eia', 'calcium', 'albumin', 'red cell antibody screening', 'ca-125 using meia', 'order rate', 'order rate', 'ct abdomen', 'First outpatient consultation', 'interc.consult clinical anesthesia', 'administrative fee - the first pol', '190021 clinical admission A002', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', 'cytology - lymfeklierpuncti', 'Upper abdominal ultrasound', 'ro gel. as ass. to puncture - biopsy l', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'telephone consultation')
    variant1, variant2 = lzw(s1), lzw(s2)
    print("Original Length: {}, {}".format(len(s1), len(s2)))
    print("New Length: {}, {}".format(len(variant1), len(variant2)))
    print(variant1)
    print(variant2)

    ds = damerau_leveshtein_distance(s1, s2)
    print("Edit distance Uncompressed: {} \t Ratio: {}".format(ds, float(ds) / max(len(s1), len(s2))))

    dc = damerau_leveshtein_distance(variant1, variant2)
    print("Edit distance COMPRESSED: {} \t Ratio: {}".format(dc, float(dc) / max(len(s1), len(s2))))
