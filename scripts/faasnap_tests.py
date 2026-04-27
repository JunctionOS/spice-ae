import json

from dirs import FUNCTIONS
from func_args import FUNCTION_ARGS
from test import Test


class FaaSnapTest(Test):
    def __init__(self, lang: str, name: str, arg_map, s3=False):
        if s3:
            d = json.loads(arg_map)
            arg_map = json.dumps(d)

        super().__init__(
            lang,
            name,
            None,  # cmd
            arg_map,
            new_version_fn=lambda x: x,
            s3=s3,
            do_second_apps=False,
        )

    def tag(self):
        return f"{self.lang}_{self.name}"

    def path(self):
        name = self.name
        if name == "chameleon" or name == "pyaes":
            name += "1"
        return f"{FUNCTIONS}/{self.lang}/{name}/{self.tag()}.tar"


class FaaSnapNodeTest(FaaSnapTest):
    def __init__(self, name, s3=False):
        super().__init__("node", name, FUNCTION_ARGS[name], s3=s3)


class FaaSnapPythonTest(FaaSnapTest):
    def __init__(self, name, s3=False):
        super().__init__("python", name, FUNCTION_ARGS[name], s3=s3)


class FaaSnapJavaTest(FaaSnapTest):
    def __init__(self, name, s3=False):
        super().__init__("java", name, FUNCTION_ARGS[name], s3=s3)


TESTS = [
    FaaSnapPythonTest("helloworld"),
    FaaSnapPythonTest("chameleon"),
    FaaSnapPythonTest("pyaes"),
    FaaSnapPythonTest("json_serdes_s3", s3=True),
    FaaSnapPythonTest("image_rotate_s3", s3=True),
    FaaSnapPythonTest("rnn_serving"),
    FaaSnapPythonTest("video_processing_s3", s3=True),
    FaaSnapPythonTest("lr_training_s3", s3=True),
    FaaSnapPythonTest("lr_serving"),
    FaaSnapPythonTest("cnn_serving"),
    FaaSnapNodeTest("image_rotate_s3", s3=True),
    FaaSnapNodeTest("json_serdes_s3", s3=True),
    FaaSnapJavaTest("image_rotate_s3", s3=True),
    FaaSnapJavaTest("matmul"),
]
