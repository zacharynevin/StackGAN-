import tensorflow as tf
from tensorflow.contrib import tpu
from tensorflow.contrib.cluster_resolver import TPUClusterResolver
from config import config
import estimator

def main(_):
    tpu_grpc_url = None

    if use_tpu:
        tpu_grpc_url = TPUClusterResolver(tpu=config.tpu_name).get_master()

    run_config = tpu.RunConfig(
        master=tpu_grpc_url,
        evaluation_master=tpu_grpc_url,
        model_dir=config.log_dir,
        session_config=tf.ConfigProto(allow_soft_placement=True,
                                      log_device_placement=True),
        tpu_config=tf.contrib.tpu.TPUConfig(config.iterations, config.num_shards)
    )

    batch_size = config.batch_size * config.tpu_shards if config.use_tpu else config.batch_size
    estimator = tpu.TPUEstimator(
        model_fn=estimator.model_fn,
        use_tpu=config.use_tpu,
        train_batch_size=batch_size,
        eval_batch_size=batch_size,
        params={
          "data_dir": config.data_dir,
          "log_dir": config.log_dir,
          "data_format": "NCHW" if config.use_tpu else "NHWC",
          "z_dim": config.z_dim,
          "num_classes": config.num_classes,
          "D_lr": config.d_lr,
          "G_lr": config.g_lr
        },
        config=run_config
    )

    estimator.train(
        input_fn=estimator.train_input_fn,
        max_steps=config.train_steps
    )

    estimator.evaluate(
        input_fn=estimator.eval_input_fn,
        steps=config.eval_steps
    )

if __name__ == '__main__':
    tf.app.run()
