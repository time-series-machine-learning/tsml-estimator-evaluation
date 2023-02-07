# -*- coding: utf-8 -*-
"""Functions to perform machine learning/data mining experiments.

Results are saved a standardised format used by tsml.
"""

__author__ = ["TonyBagnall", "MatthewMiddlehurst"]


import os
import time
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_percentage_error,
    mean_squared_error,
)
from sklearn.model_selection import cross_val_predict
from sktime.datasets import load_from_tsfile_to_dataframe

from tsml_eval.evaluation.metrics import clustering_accuracy
from tsml_eval.utils.experiments import (
    resample_data,
    stratified_resample_data,
    write_classification_results,
    write_clustering_results,
    write_forecasting_results,
    write_regression_results,
)


def run_classification_experiment(
    X_train,
    y_train,
    X_test,
    y_test,
    classifier,
    results_path,
    classifier_name=None,
    dataset_name="N/A",
    resample_id=None,
    build_test_file=True,
    build_train_file=False,
):
    """Run a classification experiment and save the results to file.

    Function to run a basic classification experiment for a
    <dataset>/<classifier/<resample> combination and write the results to csv file(s)
    at a given location.

    Parameters
    ----------
    X_train : pd.DataFrame or np.array
        The data to train the classifier.
    y_train : np.array
        Training data class labels.
    X_test : pd.DataFrame or np.array
        The data used to test the trained classifier.
    y_test : np.array
        Testing data class labels.
    classifier : BaseClassifier
        Classifier to be used in the experiment.
    results_path : str
        Location of where to write results. Any required directories will be created.
    classifier_name : str or None, default=None
        Name of classifier used in writing results. If None, the name is taken from
        the classifier.
    dataset_name : str, default="N/A"
        Name of dataset.
    resample_id : int or None, default=None
        Seed for resampling. If set to 0, the default train/test split from file is
        used. Also used in output file name.
    build_test_file : bool, default=True:
        Whether to generate test files or not. If the classifier can generate its own
        train probabilities, the classifier will be built but no file will be output.
    build_train_file : bool, default=False
        Whether to generate train files or not. If true, it performs a 10-fold
        cross-validation on the train data and saves. If the classifier can produce its
        own estimates, those are used instead.
    """
    if not build_test_file and not build_train_file:
        raise Exception(
            "Both test_file and train_file are set to False. "
            "At least one must be written."
        )

    if classifier_name is None:
        classifier_name = type(classifier).__name__

    le = preprocessing.LabelEncoder()
    y_train = le.fit_transform(y_train)
    y_test = le.transform(y_test)

    encoder_dict = {label: i for i, label in enumerate(le.classes_)}
    n_classes = len(np.unique(y_train))

    classifier_train_probs = build_train_file and callable(
        getattr(classifier, "_get_train_probs", None)
    )
    fit_time = -1

    first_comment = (
        "PREDICTIONS,Generated by run_classification_experiment on "
        f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}. "
        f"Encoder dictionary: {str(encoder_dict)}"
    )

    second = str(classifier.get_params()).replace("\n", " ").replace("\r", " ")

    if build_test_file or classifier_train_probs:
        start = int(round(time.time() * 1000))
        classifier.fit(X_train, y_train)
        fit_time = int(round(time.time() * 1000)) - start

    if build_test_file:
        start = int(round(time.time() * 1000))
        test_probs = classifier.predict_proba(X_test)
        test_time = int(round(time.time() * 1000)) - start

        test_preds = classifier.classes_[np.argmax(test_probs, axis=1)]
        test_acc = accuracy_score(y_test, test_preds)

        write_classification_results(
            test_preds,
            test_probs,
            y_test,
            classifier_name,
            dataset_name,
            results_path,
            full_path=False,
            split="TEST",
            resample_id=resample_id,
            timing_type="MILLISECONDS",
            first_line_comment=first_comment,
            parameter_info=second,
            accuracy=test_acc,
            fit_time=fit_time,
            predict_time=test_time,
            n_classes=n_classes,
        )

    if build_train_file:
        start = int(round(time.time() * 1000))
        if classifier_train_probs:  # Normally can only do this if test has been built
            train_probs = classifier._get_train_probs(X_train, y_train)
        else:
            cv_size = 10
            _, counts = np.unique(y_train, return_counts=True)
            min_class = np.min(counts)
            if min_class < cv_size:
                cv_size = min_class

            train_probs = cross_val_predict(
                classifier, X_train, y=y_train, cv=cv_size, method="predict_proba"
            )
        train_time = int(round(time.time() * 1000)) - start

        train_preds = classifier.classes_[np.argmax(train_probs, axis=1)]
        train_acc = accuracy_score(y_train, train_preds)

        write_classification_results(
            train_preds,
            train_probs,
            y_train,
            classifier_name,
            dataset_name,
            results_path,
            full_path=False,
            split="TRAIN",
            resample_id=resample_id,
            timing_type="MILLISECONDS",
            first_line_comment=first_comment,
            parameter_info=second,
            accuracy=train_acc,
            fit_time=fit_time,
            n_classes=n_classes,
            train_estimate_time=train_time,
            fit_and_estimate_time=fit_time + train_time,
        )


def load_and_run_classification_experiment(
    problem_path,
    results_path,
    dataset,
    classifier,
    resample_id=0,
    classifier_name=None,
    overwrite=False,
    build_train_file=False,
    predefined_resample=False,
):
    """Load a dataset and run a classification experiment.

    Function to load a dataset, run a basic classification experiment for a
    <dataset>/<classifier/<resample> combination, and write the results to csv file(s)
    at a given location.

    Parameters
    ----------
    problem_path : str
        Location of problem files, full path.
    results_path : str
        Location of where to write results. Any required directories will be created.
    dataset : str
        Name of problem. Files must be <problem_path>/<dataset>/<dataset>+"_TRAIN.ts",
        same for "_TEST.ts".
    classifier : BaseClassifier
        Classifier to be used in the experiment.
    classifier_name : str or None, default=None
        Name of classifier used in writing results. If None, the name is taken from
        the classifier.
    resample_id : int, default=0
        Seed for resampling. If set to 0, the default train/test split from file is
        used. Also used in output file name.
    overwrite : bool, default=False
        If set to False, this will only build results if there is not a result file
        already present. If True, it will overwrite anything already there.
    build_train_file : bool, default=False
        Whether to generate train files or not. If true, it performs a 10-fold
        cross-validation on the train data and saves. If the classifier can produce its
        own estimates, those are used instead.
    predefined_resample : bool, default=False
        Read a predefined resample from file instead of performing a resample. If True
        the file format must include the resample_id at the end of the dataset name i.e.
        <problem_path>/<dataset>/<dataset>+<resample_id>+"_TRAIN.ts".
    """
    build_test_file, build_train_file = _check_existing_results(
        results_path,
        classifier_name,
        dataset,
        resample_id,
        overwrite,
        True,
        build_train_file,
    )

    if not build_test_file and not build_train_file:
        warnings.warn("All files exist and not overwriting, skipping.")
        return

    X_train, y_train, X_test, y_test, resample = _load_data(
        problem_path, dataset, resample_id, predefined_resample
    )

    if resample:
        X_train, y_train, X_test, y_test = stratified_resample_data(
            X_train, y_train, X_test, y_test, random_state=resample_id
        )

    run_classification_experiment(
        X_train,
        y_train,
        X_test,
        y_test,
        classifier,
        results_path,
        classifier_name=classifier_name,
        dataset_name=dataset,
        resample_id=resample_id,
        build_test_file=build_test_file,
        build_train_file=build_train_file,
    )


def run_regression_experiment(
    X_train,
    y_train,
    X_test,
    y_test,
    regressor,
    results_path,
    regressor_name=None,
    dataset_name="",
    resample_id=None,
    build_test_file=True,
    build_train_file=False,
):
    """Run a regression experiment and save the results to file.

    Function to run a basic regression experiment for a
    <dataset>/<regressor/<resample> combination and write the results to csv file(s)
    at a given location.

    Parameters
    ----------
    X_train : pd.DataFrame or np.array
        The data to train the regressor.
    y_train : np.array
        Training data labels.
    X_test : pd.DataFrame or np.array
        The data used to test the trained regressor.
    y_test : np.array
        Testing data labels.
    regressor : BaseRegressor
        Regressor to be used in the experiment.
    results_path : str
        Location of where to write results. Any required directories will be created.
    regressor_name : str or None, default=None
        Name of regressor used in writing results. If None, the name is taken from
        the regressor.
    dataset_name : str, default="N/A"
        Name of dataset.
    resample_id : int or None, default=None
        Seed for resampling. If set to 0, the default train/test split from file is
        used. Also used in output file name.
    build_test_file : bool, default=True:
        Whether to generate test files or not. If the regressor can generate its own
        train predictions, the classifier will be built but no file will be output.
    build_train_file : bool, default=False
        Whether to generate train files or not. If true, it performs a 10-fold
        cross-validation on the train data and saves. If the regressor can produce its
        own estimates, those are used instead.
    """
    if not build_test_file and not build_train_file:
        raise Exception(
            "Both test_file and train_file are set to False. "
            "At least one must be written."
        )

    if regressor_name is None:
        regressor_name = type(regressor).__name__

    regressor_train_preds = build_train_file and callable(
        getattr(regressor, "_get_train_preds", None)
    )
    fit_time = -1

    first_comment = (
        "Generated by run_regression_experiment on "
        f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}"
    )

    second = str(regressor.get_params()).replace("\n", " ").replace("\r", " ")

    if build_test_file or regressor_train_preds:
        start = int(round(time.time() * 1000))
        regressor.fit(X_train, y_train)
        fit_time = int(round(time.time() * 1000)) - start

    if build_test_file:
        start = int(round(time.time() * 1000))
        test_preds = regressor.predict(X_test)
        test_time = int(round(time.time() * 1000)) - start

        test_mse = mean_squared_error(y_test, test_preds)

        write_regression_results(
            test_preds,
            y_test,
            regressor_name,
            dataset_name,
            results_path,
            full_path=False,
            split="TEST",
            resample_id=resample_id,
            timing_type="MILLISECONDS",
            first_line_comment=first_comment,
            parameter_info=second,
            mse=test_mse,
            fit_time=fit_time,
            predict_time=test_time,
        )

    if build_train_file:
        start = int(round(time.time() * 1000))
        if regressor_train_preds:  # Normally can only do this if test has been built
            train_preds = regressor._get_train_preds(X_train, y_train)
        else:
            cv_size = min(10, len(y_train))
            train_preds = cross_val_predict(regressor, X_train, y=y_train, cv=cv_size)
        train_time = int(round(time.time() * 1000)) - start

        train_mse = mean_squared_error(y_train, train_preds)

        write_regression_results(
            train_preds,
            y_train,
            regressor_name,
            dataset_name,
            results_path,
            full_path=False,
            split="TRAIN",
            resample_id=resample_id,
            timing_type="MILLISECONDS",
            first_line_comment=first_comment,
            parameter_info=second,
            mse=train_mse,
            fit_time=fit_time,
            train_estimate_time=train_time,
            fit_and_estimate_time=fit_time + train_time,
        )


def load_and_run_regression_experiment(
    problem_path,
    results_path,
    dataset,
    regressor,
    resample_id=0,
    regressor_name=None,
    overwrite=False,
    build_train_file=False,
    predefined_resample=False,
):
    """Load a dataset and run a regression experiment.

    Function to load a dataset, run a basic regression experiment for a
    <dataset>/<regressor/<resample> combination, and write the results to csv file(s)
    at a given location.

    Parameters
    ----------
    problem_path : str
        Location of problem files, full path.
    results_path : str
        Location of where to write results. Any required directories will be created.
    dataset : str
        Name of problem. Files must be <problem_path>/<dataset>/<dataset>+"_TRAIN.ts",
        same for "_TEST.ts".
    regressor : BaseRegressor
        Regressor to be used in the experiment.
    regressor_name : str or None, default=None
        Name of regressor used in writing results. If None, the name is taken from
        the regressor.
    resample_id : int, default=0
        Seed for resampling. If set to 0, the default train/test split from file is
        used. Also used in output file name.
    overwrite : bool, default=False
        If set to False, this will only build results if there is not a result file
        already present. If True, it will overwrite anything already there.
    build_train_file : bool, default=False
        Whether to generate train files or not. If true, it performs a 10-fold
        cross-validation on the train data and saves. If the regressor can produce its
        own estimates, those are used instead.
    predefined_resample : bool, default=False
        Read a predefined resample from file instead of performing a resample. If True
        the file format must include the resample_id at the end of the dataset name i.e.
        <problem_path>/<dataset>/<dataset>+<resample_id>+"_TRAIN.ts".
    """
    build_test_file, build_train_file = _check_existing_results(
        results_path,
        regressor_name,
        dataset,
        resample_id,
        overwrite,
        True,
        build_train_file,
    )

    if not build_test_file and not build_train_file:
        warnings.warn("All files exist and not overwriting, skipping.")
        return

    X_train, y_train, X_test, y_test, resample = _load_data(
        problem_path, dataset, resample_id, predefined_resample
    )

    if resample:
        X_train, y_train, X_test, y_test = resample_data(
            X_train, y_train, X_test, y_test, random_state=resample_id
        )

    # Ensure labels are floats
    y_train = y_train.astype(float)
    y_test = y_test.astype(float)

    run_regression_experiment(
        X_train,
        y_train,
        X_test,
        y_test,
        regressor,
        results_path,
        regressor_name=regressor_name,
        dataset_name=dataset,
        resample_id=resample_id,
        build_test_file=build_test_file,
        build_train_file=build_train_file,
    )


def run_clustering_experiment(
    X_train,
    y_train,
    clusterer,
    results_path,
    X_test=None,
    y_test=None,
    clusterer_name=None,
    dataset_name="N/A",
    resample_id=None,
    build_test_file=False,
    build_train_file=True,
):
    """Run a clustering experiment and save the results to file.

    Function to run a basic clustering experiment for a
    <dataset>/<clusterer/<resample> combination and write the results to csv file(s)
    at a given location.

    Parameters
    ----------
    X_train : pd.DataFrame or np.array
        The data to train the clusterer.
    y_train : np.array
        Training data class labels (used for evaluation).
    clusterer : BaseClusterer
        Clusterer to be used in the experiment.
    results_path : str
        Location of where to write results. Any required directories will be created.
    X_test : pd.DataFrame or np.array, default=None
        The data used to test the fitted clusterer.
    y_test : np.array, default=None
        Testing data class labels.
    clusterer_name : str or None, default=None
        Name of clusterer used in writing results. If None, the name is taken from
        the clusterer.
    dataset_name : str, default="N/A"
        Name of dataset.
    resample_id : int or None, default=None
        Seed for resampling. If set to 0, the default train/test split from file is
        used. Also used in output file name.
    build_test_file : bool, default=False:
        Whether to generate test files or not. If True, X_test and y_test must be
        provided.
    build_train_file : bool, default=True
        Whether to generate train files or not. The clusterer is fit using train data
        regardless of input.
    """
    if not build_test_file and not build_train_file:
        raise Exception(
            "Both test_file and train_file are set to False. "
            "At least one must be written."
        )

    if clusterer_name is None:
        clusterer_name = type(clusterer).__name__

    le = preprocessing.LabelEncoder()
    y_train = le.fit_transform(y_train)
    if y_test is not None:
        y_test = le.transform(y_test)

    encoder_dict = {label: i for i, label in enumerate(le.classes_)}
    n_classes = len(np.unique(y_train))

    start = int(round(time.time() * 1000))
    clusterer.fit(X_train)
    fit_time = int(round(time.time() * 1000)) - start

    first_comment = (
        "Generated by run_clustering_experiment on "
        f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}. "
        f"Encoder dictionary: {str(encoder_dict)}"
    )

    second = str(clusterer.get_params()).replace("\n", " ").replace("\r", " ")

    if build_train_file:
        start = int(round(time.time() * 1000))
        train_probs = clusterer.predict_proba(X_train)
        train_time = int(round(time.time() * 1000)) - start

        train_preds = np.argmax(train_probs, axis=1)
        train_acc = clustering_accuracy(y_train, train_preds)

        write_clustering_results(
            train_preds,
            train_probs,
            y_train,
            clusterer_name,
            dataset_name,
            results_path,
            full_path=False,
            split="TRAIN",
            resample_id=resample_id,
            timing_type="MILLISECONDS",
            first_line_comment=first_comment,
            parameter_info=second,
            clustering_accuracy=train_acc,
            fit_time=fit_time,
            predict_time=train_time,
            n_classes=n_classes,
            n_clusters=len(train_probs[0]),
        )

    if build_test_file:
        if X_test is None or y_test is None:
            raise Exception("Test data not provided, cannot build test file.")

        start = int(round(time.time() * 1000))
        test_probs = clusterer.predict_proba(X_test)
        test_time = int(round(time.time() * 1000)) - start

        test_preds = np.argmax(test_probs, axis=1)
        test_acc = clustering_accuracy(y_test, test_preds)

        write_clustering_results(
            test_preds,
            test_probs,
            y_test,
            clusterer_name,
            dataset_name,
            results_path,
            full_path=False,
            split="TEST",
            resample_id=resample_id,
            timing_type="MILLISECONDS",
            first_line_comment=first_comment,
            parameter_info=second,
            clustering_accuracy=test_acc,
            fit_time=fit_time,
            predict_time=test_time,
            n_classes=n_classes,
            n_clusters=len(test_probs[0]),
        )


def load_and_run_clustering_experiment(
    problem_path,
    results_path,
    dataset,
    clusterer,
    resample_id=0,
    clusterer_name=None,
    overwrite=False,
    build_test_file=False,
    predefined_resample=False,
):
    """Load a dataset and run a clustering experiment.

    Function to load a dataset, run a basic clustering experiment for a
    <dataset>/<clusterer/<resample> combination, and write the results to csv file(s)
    at a given location.

    Parameters
    ----------
    problem_path : str
        Location of problem files, full path.
    results_path : str
        Location of where to write results. Any required directories will be created.
    dataset : str
        Name of problem. Files must be <problem_path>/<dataset>/<dataset>+"_TRAIN.ts",
        same for "_TEST.ts".
    clusterer : BaseClusterer
        Clusterer to be used in the experiment.
    resample_id : int, default=0
        Seed for resampling. If set to 0, the default train/test split from file is
        used. Also used in output file name.
    clusterer_name : str or None, default=None
        Name of clusterer used in writing results. If None, the name is taken from
        the clusterer.
    overwrite : bool, default=False
        If set to False, this will only build results if there is not a result file
        already present. If True, it will overwrite anything already there.
    build_test_file : bool, default=False
        Whether to generate test files or not. If true, the clusterer will assign
        clusters to the loaded test data.
    predefined_resample : bool, default=False
        Read a predefined resample from file instead of performing a resample. If True
        the file format must include the resample_id at the end of the dataset name i.e.
        <problem_path>/<dataset>/<dataset>+<resample_id>+"_TRAIN.ts".
    """
    build_test_file, build_train_file = _check_existing_results(
        results_path,
        clusterer_name,
        dataset,
        resample_id,
        overwrite,
        build_test_file,
        True,
    )

    if not build_test_file and not build_train_file:
        warnings.warn("All files exist and not overwriting, skipping.")
        return

    X_train, y_train, X_test, y_test, resample = _load_data(
        problem_path, dataset, resample_id, predefined_resample
    )

    if resample:
        X_train, y_train, X_test, y_test = stratified_resample_data(
            X_train, y_train, X_test, y_test, random_state=resample_id
        )

    run_clustering_experiment(
        X_train,
        y_train,
        clusterer,
        results_path,
        X_test=X_test,
        y_test=y_test,
        clusterer_name=clusterer_name,
        dataset_name=dataset,
        resample_id=resample_id,
        build_train_file=build_train_file,
        build_test_file=build_test_file,
    )


def run_forecasting_experiment(
    train,
    test,
    forecaster,
    results_path,
    forecaster_name=None,
    dataset_name="",
    resample_id=None,
):
    """Run a regression experiment and save the results to file.

    Function to run a basic regression experiment for a
    <dataset>/<regressor/<resample> combination and write the results to csv file(s)
    at a given location.

    Parameters
    ----------
    X_train : pd.DataFrame or np.array
        The data to train the regressor.
    y_train : np.array
        Training data labels.
    X_test : pd.DataFrame or np.array
        The data used to test the trained regressor.
    y_test : np.array
        Testing data labels.
    regressor : BaseRegressor
        Regressor to be used in the experiment.
    results_path : str
        Location of where to write results. Any required directories will be created.
    regressor_name : str or None, default=None
        Name of regressor used in writing results. If None, the name is taken from
        the regressor.
    dataset_name : str, default="N/A"
        Name of dataset.
    resample_id : int or None, default=None
        Seed for resampling. If set to 0, the default train/test split from file is
        used. Also used in output file name.
    build_test_file : bool, default=True:
        Whether to generate test files or not. If the regressor can generate its own
        train predictions, the classifier will be built but no file will be output.
    build_train_file : bool, default=False
        Whether to generate train files or not. If true, it performs a 10-fold
        cross-validation on the train data and saves. If the regressor can produce its
        own estimates, those are used instead.
    """
    if forecaster_name is None:
        forecaster_name = type(forecaster).__name__

    first_comment = (
        "Generated by run_forecasting_experiment on "
        f"{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}"
    )

    second = str(forecaster.get_params()).replace("\n", " ").replace("\r", " ")

    start = int(round(time.time() * 1000))
    forecaster.fit(train)
    fit_time = int(round(time.time() * 1000)) - start

    start = int(round(time.time() * 1000))
    test_preds = forecaster.predict(np.arange(1, len(test) + 1))
    test_time = int(round(time.time() * 1000)) - start
    test_preds = test_preds.flatten()

    test_mape = mean_absolute_percentage_error(test, test_preds)

    write_forecasting_results(
        test_preds,
        test,
        forecaster_name,
        dataset_name,
        results_path,
        full_path=False,
        split="TEST",
        resample_id=resample_id,
        timing_type="MILLISECONDS",
        first_line_comment=first_comment,
        parameter_info=second,
        mape=test_mape,
        fit_time=fit_time,
        predict_time=test_time,
    )


def load_and_run_forecasting_experiment(
    problem_path,
    results_path,
    dataset,
    forecaster,
    resample_id=0,
    forecaster_name=None,
    overwrite=False,
):
    """Load a dataset and run a regression experiment.

    Function to load a dataset, run a basic regression experiment for a
    <dataset>/<regressor/<resample> combination, and write the results to csv file(s)
    at a given location.

    Parameters
    ----------
    problem_path : str
        Location of problem files, full path.
    results_path : str
        Location of where to write results. Any required directories will be created.
    dataset : str
        Name of problem. Files must be <problem_path>/<dataset>/<dataset>+"_TRAIN.ts",
        same for "_TEST.ts".
    regressor : BaseRegressor
        Regressor to be used in the experiment.
    regressor_name : str or None, default=None
        Name of regressor used in writing results. If None, the name is taken from
        the regressor.
    resample_id : int, default=0
        Seed for resampling. If set to 0, the default train/test split from file is
        used. Also used in output file name.
    overwrite : bool, default=False
        If set to False, this will only build results if there is not a result file
        already present. If True, it will overwrite anything already there.
    """
    build_test_file, _ = _check_existing_results(
        results_path,
        forecaster_name,
        dataset,
        resample_id,
        overwrite,
        True,
        False,
    )

    if not build_test_file:
        warnings.warn("All files exist and not overwriting, skipping.")
        return

    train = pd.read_csv(
        f"{problem_path}/{dataset}/{dataset}_TRAIN.csv", index_col=0
    ).squeeze("columns")
    train = train.astype(float).to_numpy()
    test = pd.read_csv(
        f"{problem_path}/{dataset}/{dataset}_TEST.csv", index_col=0
    ).squeeze("columns")
    test = test.astype(float).to_numpy()

    run_forecasting_experiment(
        train,
        test,
        forecaster,
        results_path,
        forecaster_name=forecaster_name,
        dataset_name=dataset,
        resample_id=resample_id,
    )


def _check_existing_results(
    results_path,
    estimator_name,
    dataset,
    resample_id,
    overwrite,
    build_test_file,
    build_train_file,
):
    if not overwrite:
        resample_str = "Result" if resample_id is None else f"Resample{resample_id}"

        if build_test_file:
            full_path = (
                f"{results_path}/{estimator_name}/Predictions/{dataset}/"
                f"/test{resample_str}.csv"
            )

            if os.path.exists(full_path):
                build_test_file = False

        if build_train_file:
            full_path = (
                f"{results_path}/{estimator_name}/Predictions/{dataset}/"
                f"/train{resample_str}.csv"
            )

            if os.path.exists(full_path):
                build_train_file = False

    return build_test_file, build_train_file


def _load_data(problem_path, dataset, resample_id, predefined_resample):
    if resample_id is not None and predefined_resample:
        resample_str = "" if resample_id is None else str(resample_id)

        X_train, y_train = load_from_tsfile_to_dataframe(
            f"{problem_path}/{dataset}/{dataset}{resample_str}_TRAIN.ts"
        )
        X_test, y_test = load_from_tsfile_to_dataframe(
            f"{problem_path}/{dataset}/{dataset}{resample_str}_TEST.ts"
        )

        resample_data = False
    else:
        X_train, y_train = load_from_tsfile_to_dataframe(
            f"{problem_path}/{dataset}/{dataset}_TRAIN.ts"
        )
        X_test, y_test = load_from_tsfile_to_dataframe(
            f"{problem_path}/{dataset}/{dataset}_TEST.ts"
        )

        resample_data = True if resample_id != 0 else False

    return X_train, y_train, X_test, y_test, resample_data
