# -*- coding: utf-8 -*-
"""Variability

This module defines three different function to compute variability of a EventLog (pm4py.objects.log.EventLog)
"""
from pm4py.objects.log import log as lg
from itertools import combinations
from collections import Counter
import editdistance


def compute_variant_variability(log: lg.EventLog) -> int:
    """Compute the number of variants present of the event log

    Args:
        log (EventLog): The log to examine

    Returns:
        int: The number of variants present of the event log
    """
    return len(set(tuple(event["concept:name"] for event in case) for case in log))


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


def compute_my_variability(log: lg.EventLog):
    variants_with_repetitions = [
        tuple(event["concept:name"] for event in case) for case in log
    ]
    variants_and_n_of_occurrences = Counter(variants_with_repetitions)

    sum_of_distances = 0
    sum_of_max_distances = 0
    for (variant1, num_of_items_1), (variant2, num_of_items_2) in combinations(
            variants_and_n_of_occurrences.items(), 2
    ):
        sum_of_distances += num_of_items_1 * num_of_items_2 * editdistance.eval(variant1, variant2) * 2
        sum_of_max_distances += num_of_items_1 * num_of_items_2 * max(len(variant1), len(variant2)) * 2

    sum_of_max_distances += (
            sum(len(k) * v * (v - 1) for k, v in variants_and_n_of_occurrences.items())
    )
    return 1 - (float(sum_of_distances) / sum_of_max_distances)


if __name__ == "__main__":
    s1 = ('assumption laboratory', 'assumption laboratory', 'assumption laboratory', 'unconjugated bilirubin', 'bilirubin - total', 'glucose', 'urea', 'hemoglobin photoelectric', 'creatinine', 'alkaline phosphatase-kinetic-', 'sodium flame photometry', 'potassium potentiometrically', 'SGOT - Asat kinetic', 'SGPT - alat kinetic', 'Milk acid dehydrogenase LDH kinetic', 'ABO blood group and rhesus factor', 'rhesus factor d - Centrifuge method - email', 'leukocyte count electronic', 'platelet count - Electronic', 'gammaglutamyltranspeptidase', 'CEA - tumor marker using meia', 'calcium', 'albumin', 'red cell antibody screening', 'ca-125 using meia', 'differentiation leukocytes - manual', 'order rate', 'First outpatient consultation', 'administrative fee - the first pol', 'thorax', 'thorax', 'ct abdomen', 'ct abdomen', 'demurrage - all spec.beh.kinderg.-Reval.', 'assumption laboratory', 'assumption laboratory', 'assumption laboratory', 'urea', 'hemoglobin photoelectric', 'creatinine', 'sodium flame photometry', 'potassium potentiometrically', 'ABO blood group and rhesus factor', 'rhesus factor d - Centrifuge method - email', 'differential count automatically', 'leukocyte count electronic', 'platelet count - Electronic', 'red cell antibody screening', 'order rate', '190021 clinical admission A002', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', 'ovarian - ovarian redebulking CarCine', 'immuno-pathology', 'immuno-pathology', 'cytology - ascites -', 'histological examination - big resectiep', 'assumption laboratory', 'assumption laboratory', 'assumption laboratory', 'glucose', 'glucose', 'methemoglobin - sulphemoglobin each', 'hemoglobin photoelectric', 'hemoglobin photoelectric', 'bicarbonate', 'Co-hb kwn.', 'sodium flame photometry', 'sodium flame photometry', 'potassium potentiometrically', 'potassium potentiometrically', 'platelet count - Electronic', 'cefalinetijd - coagulation', 'Current ph - PCO2 - stand.bicarbonaat', 'crossmatch methods, three fully-', 'crossmatch methods, three fully-', 'lactic acid enzymatic', 'lactic acid enzymatic', 'calcium', 'calcium', 'O2 saturation', 'O2 saturation', 'prothrombin', 'order rate', 'order rate', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'filtered red cells', 'demurrage - all spec.beh.kinderg.-Reval.', 'assumption laboratory', 'assumption laboratory', 'urea', 'hemoglobin photoelectric', 'creatinine', 'sodium flame photometry', 'potassium potentiometrically', 'SGOT - Asat kinetic', 'SGPT - alat kinetic', 'leukocyte count electronic', 'platelet count - Electronic', 'gammaglutamyltranspeptidase', 'CRP c-reactive protein', 'order rate', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', 'assumption laboratory', 'assumption laboratory', 'hemoglobin photoelectric', 'creatinine', 'sodium flame photometry', 'potassium potentiometrically', 'order rate', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'telephone consultation')
    s2 = ('demurrage - all spec.beh.kinderg.-Reval.', 'assumption laboratory', 'assumption laboratory', 'assumption laboratory', 'unconjugated bilirubin', 'bilirubin - total', 'glucose', 'urea', 'hemoglobin photoelectric', 'creatinine', 'alkaline phosphatase-kinetic-', 'sodium flame photometry', 'potassium potentiometrically', 'SGOT - Asat kinetic', 'SGPT - alat kinetic', 'Milk acid dehydrogenase LDH kinetic', 'ABO blood group and rhesus factor', 'rhesus factor d - Centrifuge method - email', 'leukocyte count electronic', 'platelet count - Electronic', 'gammaglutamyltranspeptidase', 'CEA - tumor marker using meia', 'squamous cell carcinoma using eia', 'calcium', 'albumin', 'red cell antibody screening', 'ca-125 using meia', 'order rate', 'order rate', 'ct abdomen', 'First outpatient consultation', 'interc.consult clinical anesthesia', 'administrative fee - the first pol', '190021 clinical admission A002', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', 'cytology - lymfeklierpuncti', 'Upper abdominal ultrasound', 'ro gel. as ass. to puncture - biopsy l', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'demurrage - all spec.beh.kinderg.-Reval.', '190205 Class 3b A205', '190101 reg.toesl above. A101', 'telephone consultation')

