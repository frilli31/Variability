#!/usr/bin/env python3
from pm4py.objects.log.importer.xes import factory as xes_import_factory
from variability import *

if __name__ == "__main__":
    log_path = 'resources/exercise2.xes'
    log = xes_import_factory.apply(log_path)
    print(Counter(tuple(event["concept:name"] for event in case) for case in log))
    print(compute_variant_variability(log))
    print(compute_edit_distance_variability(log))
    print(compute_my_variability(log))
