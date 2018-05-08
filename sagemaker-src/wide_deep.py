from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os
import shutil
import sys

import tensorflow as tf  


_fields = [
 'trafficsource_referralpath',
 'geonetwork_city',
 'geonetwork_country',
 'geonetwork_region',
 'geonetwork_metro',
 'device_browser',
 'trafficsource_campaign',
 'trafficsource_source',
 'trafficsource_medium',
 'device_mobiledevicemodel',
 'device_operatingsystemversion',
 'hits_appinfo_appname',
 'hits_appinfo_appversion',
 'hits_appinfo_screenname',
 'hits_page_pagetitle',
 'hits_page_pagepath'
]
_metrics = [
    'pageviews',
    'screenviews'
]
_label = ['article_consumption_level']

_fields_defaults = [['']] * len(_fields)
_metrics_defaults = [[0]] * len(_metrics)
_target_labels_idx = {
    '50': 0,
    '75': 1,
    '100': 2
}
_CSV_COLUMNS = _fields + _metrics + _label
_CSV_COLUMN_DEFAULTS = _fields_defaults + _metrics_defaults + [[0]]
_NUM_EXAMPLES = {
    'train': 20000,
    'validation': 10000,
}
LOSS_PREFIX = {'wide': 'linear/', 'deep': 'dnn/'}

batch_size = 64
model_dir = "./model_dir/"
model_type = 'wide+deep'
# model_type = 'wide'
# model_type = 'deep'
data_dir = './data/'

train_epochs = 20
epochs_between_evals = 10

train_f = os.path.join(data_dir, 'scroll_traffic.train.small')
validate_f = os.path.join(data_dir, 'scroll_traffic.valid.small')
test_f = os.path.join(data_dir, 'scroll_traffic.test.small')

def build_model_columns():
    """
        Builds a set of wide and deep feature columns.
    """
    # Continuous columns

    pageviews = tf.feature_column.numeric_column('pageviews')
    screenviews = tf.feature_column.numeric_column('screenviews')

    geonetwork_country = tf.feature_column.categorical_column_with_hash_bucket(
        'geonetwork_country', hash_bucket_size=200)
    geonetwork_region = tf.feature_column.categorical_column_with_hash_bucket(
        'geonetwork_region', hash_bucket_size=500)
#     hits_hour = tf.feature_column.categorical_column_with_hash_bucket(
#         'hits_hour', hash_bucket_size=20
#     )
    trafficsource_referralpath = tf.feature_column.categorical_column_with_hash_bucket(
        'trafficsource_referralpath', hash_bucket_size=25000)
    geonetwork_city = tf.feature_column.categorical_column_with_hash_bucket(
        'geonetwork_city', hash_bucket_size=5000)
    geonetwork_metro = tf.feature_column.categorical_column_with_hash_bucket(
        'geonetwork_metro', hash_bucket_size=200)
    device_browser = tf.feature_column.categorical_column_with_hash_bucket(
        'device_browser', hash_bucket_size=200)
    trafficsource_campaign = tf.feature_column.categorical_column_with_hash_bucket(
        'trafficsource_campaign', hash_bucket_size=10000)
    trafficsource_source = tf.feature_column.categorical_column_with_hash_bucket(
        'trafficsource_source', hash_bucket_size=200)
    trafficsource_medium = tf.feature_column.categorical_column_with_hash_bucket(
        'trafficsource_medium', hash_bucket_size=300)
    device_mobiledevicemodel = tf.feature_column.categorical_column_with_hash_bucket(
        'device_mobiledevicemodel', hash_bucket_size=500)
    device_operatingsystemversion = tf.feature_column.categorical_column_with_hash_bucket(
        'device_operatingsystemversion', hash_bucket_size=100)
    hits_appinfo_appname = tf.feature_column.categorical_column_with_hash_bucket(
        'hits_appinfo_appname', hash_bucket_size=500)
    hits_appinfo_appversion = tf.feature_column.categorical_column_with_hash_bucket(
        'hits_appinfo_appversion', hash_bucket_size=25)
    hits_appinfo_screenname = tf.feature_column.categorical_column_with_hash_bucket(
        'hits_appinfo_screenname', hash_bucket_size=12000)
    hits_page_pagetitle = tf.feature_column.categorical_column_with_hash_bucket(
        'hits_page_pagetitle', hash_bucket_size=18000)
    hits_page_pagepath = tf.feature_column.categorical_column_with_hash_bucket(
        'hits_page_pagepath', hash_bucket_size=15000)

    # Wide columns and deep columns.
    base_columns = [
        pageviews, screenviews, geonetwork_region, geonetwork_city, geonetwork_metro, geonetwork_country, 
        device_browser, trafficsource_campaign, trafficsource_source, trafficsource_medium, device_mobiledevicemodel,
        device_operatingsystemversion, hits_appinfo_appname, hits_appinfo_appversion, hits_appinfo_screenname,
        hits_page_pagetitle, hits_page_pagepath, trafficsource_referralpath
    ]

    crossed_columns = [
      tf.feature_column.crossed_column(
          ['hits_appinfo_appname', 'hits_appinfo_appversion'], hash_bucket_size=5000),
      tf.feature_column.crossed_column(
          ['geonetwork_city', 'hits_page_pagepath'], hash_bucket_size=25000),
      tf.feature_column.crossed_column(
          ['geonetwork_city', 'geonetwork_metro'], hash_bucket_size=25000)
    ]

    wide_columns = base_columns + crossed_columns

    deep_columns = [
        pageviews,
        screenviews,
        tf.feature_column.embedding_column(geonetwork_metro, dimension=8),
        tf.feature_column.embedding_column(geonetwork_city, dimension=8),
        tf.feature_column.embedding_column(geonetwork_country, dimension=8),
        tf.feature_column.embedding_column(device_browser, dimension=8),
        tf.feature_column.embedding_column(trafficsource_source, dimension=8),
        tf.feature_column.embedding_column(trafficsource_campaign, dimension=8),
        tf.feature_column.embedding_column(device_operatingsystemversion, dimension=8),
        tf.feature_column.embedding_column(device_mobiledevicemodel, dimension=8),
        tf.feature_column.embedding_column(hits_appinfo_appname, dimension=8),
        tf.feature_column.embedding_column(hits_appinfo_appversion, dimension=8),
        tf.feature_column.embedding_column(hits_page_pagetitle, dimension=8),
        tf.feature_column.embedding_column(hits_page_pagepath, dimension=8),
        tf.feature_column.embedding_column(trafficsource_referralpath, dimension=8),
        tf.feature_column.embedding_column(trafficsource_medium, dimension=8)
    ]

    return wide_columns, deep_columns

def build_estimator(model_dir, model_type):
    """Build an estimator appropriate for the given model type."""
    wide_columns, deep_columns = build_model_columns()
    hidden_units = [20, 15, 10, 5]

  # Create a tf.estimator.RunConfig to ensure the model is run on CPU, which
  # trains faster than GPU for this model.
    run_config = tf.estimator.RunConfig().replace(
      session_config=tf.ConfigProto(device_count={'GPU': 0}))

    if model_type == 'wide':
        print('wide')
        return tf.estimator.LinearClassifier(
            model_dir=model_dir,
            n_classes=3,
            feature_columns=wide_columns,
            config=run_config)
    elif model_type == 'deep':
        print('deep')
        return tf.estimator.DNNClassifier(
            model_dir=model_dir,
            n_classes=3,
            feature_columns=deep_columns,
            hidden_units=hidden_units,
            config=run_config)
    else:
        print ("wide + deep")
        return tf.estimator.DNNLinearCombinedClassifier(
            model_dir=model_dir,
            n_classes=3,
            linear_optimizer=tf.train.FtrlOptimizer(
                learning_rate=0.01,
                l1_regularization_strength=0.0001,
                l2_regularization_strength=0.01),
            linear_feature_columns=wide_columns,
            dnn_feature_columns=deep_columns,
            dnn_hidden_units=hidden_units,
            config=run_config)


def input_fn(data_file, num_epochs=25, shuffle=False, batch_size=128):
    """Generate an input function for the Estimator."""
#     assert tf.gfile.Exists(data_file), (
#       '%s not found. Please make sure you have run data_download.py and '
#       'set the --data_dir argument to the correct path.' % data_file)

    def parse_csv(value):
        print('Parsing', data_file)
        columns = tf.decode_csv(value, field_delim='|', record_defaults=_CSV_COLUMN_DEFAULTS)
        features = dict(zip(_CSV_COLUMNS, columns))
        labels = features.pop('article_consumption_level')
        return features, labels

    # Extract lines from input files using the Dataset API.
    dataset = tf.data.TextLineDataset(data_file)

    if shuffle:
        dataset = dataset.shuffle(buffer_size=_NUM_EXAMPLES['train'])

    dataset = dataset.map(parse_csv, num_parallel_calls=4)

    # We call repeat after shuffling, rather than before, to prevent separate
    # epochs from blending together.
    dataset = dataset.repeat(num_epochs)
    dataset = dataset.batch(batch_size)
    return dataset

def train_input_fn():
    return input_fn(
        os.path.join(data_dir, 'scroll_traffic.train.small'), epochs_between_evals, True, batch_size)

def eval_input_fn():
    return input_fn(os.path.join(data_dir, 'scroll_traffic.valid.small'), 1, False, batch_size)

def test_input_fn():
    return input_fn(os.path.join(data_dir, 'scroll_traffic.test.small'), 1, False, batch_size)

# def serving_input_fn():
#     serving_columns = [
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.VarLenFeature(dtype=tf.string),
#     tf.FixedLenFeature(dtype=tf.int64, shape=[1], default_value=0),
#     tf.FixedLenFeature(dtype=tf.int64, shape=[1], default_value=0),
# ]
#     features = dict(zip(_CSV_COLUMNS[:-1], serving_columns))
#     return tf.estimator.export.build_parsing_serving_input_receiver_fn(features)()

def serving_input_receiver_fn():
    """An input receiver that expects a serialized tf.Example."""
    serving_columns = [
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.VarLenFeature(dtype=tf.string),
        tf.FixedLenFeature(dtype=tf.int64, shape=[1], default_value=0),
        tf.FixedLenFeature(dtype=tf.int64, shape=[1], default_value=0),
]
    features = dict(zip(_CSV_COLUMNS[:-1], serving_columns))
    serialized_tf_example = tf.placeholder(dtype=tf.string,
                                         shape=[1],
                                         name='input_example_tensor')
    receiver_tensors = {'examples': serialized_tf_example}
    features = tf.parse_example(serialized_tf_example, features)
    return tf.estimator.export.ServingInputReceiver(features, receiver_tensors)
