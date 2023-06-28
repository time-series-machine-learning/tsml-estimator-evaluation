# -*- coding: utf-8 -*-
"""Estimators not present in tsml or sktime."""

__all__ = [
    "SklearnToTsmlClassifier",
    "SklearnToTsmlClusterer",
    "SklearnToTsmlRegressor",
]

from tsml_eval.estimators.classification._sklearn_classifier import (
    SklearnToTsmlClassifier,
)
from tsml_eval.estimators.clustering._sklearn_clusterer import SklearnToTsmlClusterer
from tsml_eval.estimators.regression._sklearn_regressor import SklearnToTsmlRegressor
