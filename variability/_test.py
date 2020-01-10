import pytest
from pm4py.objects.log.importer.xes import factory as xes_import_factory
from main import compute_variant_variability, compute_edit_distance_variability
from pm4py.algo.filtering.log.variants import variants_filter
import os

RESOURCE_FOLDER = "./resources/"


@pytest.mark.parametrize("log_name", os.listdir(RESOURCE_FOLDER))
def test_variant_variability(log_name):
    log = xes_import_factory.apply(RESOURCE_FOLDER+log_name)
    assert compute_variant_variability(log) == len(variants_filter.get_variants(log))


def test_edit_distance_variability():
    log_path = RESOURCE_FOLDER + "L3.xes"
    log = xes_import_factory.apply(log_path)
    assert compute_edit_distance_variability(log) == float(5.833333333333333)
