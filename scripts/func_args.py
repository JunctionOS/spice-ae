import json

from args import ARGS
from minio_helper import prefix_fbench


def to_json_string(**args):
    return json.dumps(args)


FUNC_LABEL_MAP = {
    "python_helloworld": "hello",
    "python_pyaes": "pyaes",
    "java_matmul": "mtml",
    "python_chameleon": "html",
    "python_image_rotate_s3": "img",
    "python_json_serdes_s3": "json",
    "node_json_serdes_s3": "json",
    "python_lr_serving": "lr",
    "python_rnn_serving": "rnn",
    "python_cnn_serving": "cnn",
    "node_image_rotate_s3": "img",
    "python_video_processing_s3": "video",
    "java_image_rotate_s3": "img",
}


def get_label(f):
    return FUNC_LABEL_MAP.get(f)


if ARGS.do_faasnap or ARGS.do_reap:

    def prefix_fbench(string):
        return "/app/data/" + string


FUNCTION_ARGS = {
    "helloworld": to_json_string(message="Hello, world!"),
    "chameleon": to_json_string(num_of_rows=10, num_of_cols=10),
    "pyaes": to_json_string(length_of_message=100, num_of_iterations=3),
    "json_serdes_s3": to_json_string(json_file="1.json"),
    "image_rotate_s3": to_json_string(image="img3.jpeg"),
    "rnn_serving": to_json_string(
        language="Scottish",
        start_letters="ABCDEFGHIJKLMNOP",
        parameter_path=prefix_fbench("ml/rnn_params.pkl"),
        model_path=prefix_fbench("ml/rnn_model.pth"),
    ),
    "video_processing_s3": to_json_string(vid="vid1.mp4"),
    "lr_training_s3": to_json_string(data="dataset2.csv"),
    "lr_serving": to_json_string(
        prompt="My favorite cafe. I like going there on weekends, always taking a cafe and some of their pastry before visiting my parents.  ",
        dataset_path=prefix_fbench("ml/dataset.csv"),
        model_path=prefix_fbench("ml/lr_model.pk"),
    ),
    "cnn_serving": to_json_string(
        img_path=prefix_fbench("images/image.jpg"),
        img2_path=prefix_fbench("images/image.jpg"),
        model_path=prefix_fbench("ml/squeezenet_weights_tf_dim_ordering_tf_kernels.h5"),
        class_index_path=prefix_fbench("ml/imagenet_class_index.json"),
    ),
    "matmul": to_json_string(N=1100),
}
