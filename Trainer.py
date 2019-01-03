from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
from datetime import datetime

tf.logging.set_verbosity(tf.logging.INFO)



train_data = None
eval_data = None
train_labels = None
eval_labels = None



def cnn_model_fn(features, labels, mode):
    """Model function for CNN."""
    # Input Layer
    # Reshape X to 4-D tensor: [batch_size, binarPositions, labels]
    input_layer = tf.reshape(features["x"], [-1, 5, 5, 3])
    #input_layer = tf.cast(input_layer, tf.float32)
    #if(labels != None):
    #    labels = tf.cast(labels, tf.float32)


    # Convolutional Layer #1
    conv1 = tf.layers.conv2d(
        inputs=input_layer,
        filters=32,
        kernel_size=[2, 2],
        #padding="same",
        activation=tf.nn.relu)

    pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)

    pool1_flat = tf.reshape(pool1, [-1, 2* 2 * 32])

    # Dense Layer Densely connected layer
    dense = tf.layers.dense(inputs=pool1_flat, units=1000, activation=tf.nn.relu)

    

    # Logits layer
    logits = tf.layers.dense(inputs=dense, units=9)

    predictions = {
        # Generate predictions (for PREDICT and EVAL mode)
        "round_results": tf.round(logits),
        "results": logits #tf.where(labels > 0, logits, tf.zeros_like(logits)), # tf.argmax(input=logits, axis=1),
        # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
        # `logging_hook`.
        #"probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }


    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    # Calculate Loss (for both TRAIN and EVAL modes)
    #loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
    loss = tf.reduce_mean(tf.abs(labels-logits))

    # Configure the Training Op (for TRAIN mode)
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
        train_op = optimizer.minimize(
            loss=loss,
            global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

    # Add evaluation metrics (for EVAL mode)
    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
            labels=labels, predictions=predictions["results"])}
    return tf.estimator.EstimatorSpec(
        mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


def getModelDir(isPrey):
    if isPrey:
        return "/D/Projects/TensorFlow/PredatorPrey/PreyModel"
    else: 
        return "/D/Projects/TensorFlow/PredatorPrey/PredModel"


def train( _data, _labels, isPrey, modelInitialization):
    
    modelDir = getModelDir(isPrey)

    # Create the Estimator
    mnist_classifier = tf.estimator.Estimator(
        model_fn=cnn_model_fn, 
        model_dir=modelDir)

    # Set up logging for predictions
    # Log the values in the "Softmax" tensor with label "probabilities"
    #tensors_to_log = {"probabilities": "softmax_tensor"}
    tensors_to_log = {}
    logging_hook = tf.train.LoggingTensorHook(
        tensors=tensors_to_log, every_n_iter=100)

    # Train the model
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": _data},
        y=_labels,
        batch_size=100 if not modelInitialization else 1,
        num_epochs=None,
        shuffle=True)
    mnist_classifier.train(
        input_fn=train_input_fn,
        steps=4000 if not modelInitialization else 1,
        hooks=[logging_hook])

    # Evaluate the model and print results
    eval_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": _data},
        y=_labels,
        num_epochs=1,
        shuffle=False)
    eval_results = mnist_classifier.evaluate(input_fn=eval_input_fn)
    
    return eval_results

def predict( _data, isPrey):
    modelDir = getModelDir(isPrey)

    # Create the Estimator
    mnist_classifier = tf.estimator.Estimator(
        model_fn=cnn_model_fn, 
        model_dir=modelDir)

    # Evaluate the model and print results
    eval_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": _data},
        #y=eval_labels,
        num_epochs=1,
        shuffle=False)
    eval_results = mnist_classifier.predict(input_fn=eval_input_fn)
    #for result in eval_results:
    #    print('result: {}'.format(result)) 
    #print(eval_results)
    directions = []
    allDir = []
    for result in eval_results: 
        allDir.append(result.get("round_results"))
        directions.append(np.argmax(result.get("results")))
    return directions
