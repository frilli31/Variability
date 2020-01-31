import pytest
from pm4py.objects.log.importer.xes import factory as xes_import_factory
from main import compute_variant_variability, compute_edit_distance_variability, compute_my_variability
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


def test_edit_distance_variability_single_variant():
    log_path = RESOURCE_FOLDER + "single_variant.xes"
    log = xes_import_factory.apply(log_path)
    assert compute_edit_distance_variability(log) == float(0)


def test_edit_distance_variability_different_traces():
    log_path = RESOURCE_FOLDER + "different_traces.xes"
    log = xes_import_factory.apply(log_path)
    assert compute_edit_distance_variability(log) == float(1)


def test_my_variability():
    log_path = RESOURCE_FOLDER + "L3.xes"
    log = xes_import_factory.apply(log_path)
    assert compute_my_variability(log) == float(0.5880681818181819)


def test_my_variability_single_variant():
    log_path = RESOURCE_FOLDER + "single_variant.xes"
    log = xes_import_factory.apply(log_path)
    assert compute_my_variability(log) == float(1)


def test_my_variability_different_traces():
    log_path = RESOURCE_FOLDER + "different_traces.xes"
    log = xes_import_factory.apply(log_path)
    assert compute_my_variability(log) == float(0)
