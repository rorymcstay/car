import tensorflow as tf
from tensorflow.contrib.boosted_trees.estimator_batch.estimator import GradientBoostedDecisionTreeClassifier
from tensorflow.contrib.boosted_trees.proto import learner_pb2 as gbdt_learner

from src.main.dataframe.api import CarManager

# Parameters
batch_size = 4096 # The number of samples per batch
num_classes = 10 # The 10 digits
num_features = 784 # Each image is 28x28 pixels
max_steps = 10000

# GBDT Parameters
learning_rate = 0.1
l1_regul = 0.
l2_regul = 1.
examples_per_layer = 1000
num_trees = 10
max_depth = 16

learner_config = gbdt_learner.LearnerConfig()
learner_config.learning_rate_tuner.fixed.learning_rate = learning_rate
learner_config.regularization.l1 = l1_regul
learner_config.regularization.l2 = l2_regul / examples_per_layer
learner_config.constraints.max_tree_depth = max_depth
growing_mode = gbdt_learner.LearnerConfig.LAYER_BY_LAYER
learner_config.growing_mode = growing_mode
run_config = tf.contrib.learn.RunConfig(save_checkpoints_secs=300)
learner_config.multi_class_strategy = (gbdt_learner.LearnerConfig.DIAGONAL_HESSIAN)

gbdt_model = GradientBoostedDecisionTreeClassifier(
    model_dir=None,  # No save directory specified
    learner_config=learner_config,
    n_classes=num_classes,
    examples_per_layer=examples_per_layer,
    num_trees=num_trees,
    center_bias=False,
    config=run_config)

carManager = CarManager()
data = carManager.getDataframe()
target = data['price']
features = data.drop(columns='price')


# https://www.tensorflow.org/api_docs/python/tf/estimator/inputs/pandas_input_fn
input_fn = tf.estimator.inputs.pandas_input_fn(
    x=features, y=target,
    batch_size=batch_size, num_epochs=None, shuffle=True)

gbdt_model.fit(input_fn=input_fn, max_steps=max_steps)

e = gbdt_model.evaluate(input_fn=input_fn)

print("Testing Accuracy:", e['accuracy'])
