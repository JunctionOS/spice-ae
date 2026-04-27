import re

from args import ARGS


class Test:
    @classmethod
    def template(
        cls,
        lang: str,
        name: str,
        cmd: str,
        arg_map,
        new_version_fn=lambda x: x,
        env="",
        s3=False,
        do_second_apps=True,
    ):
        """
        punch out a template of tests, where the arg_map is a map from arg_name -> arg
        return a list of Tests
        """
        return [
            cls(lang, name, cmd, args, arg_name, new_version_fn, env=env)
            for arg_name, args in arg_map.items()
        ]

    def __init__(
        self,
        lang: str,
        name: str,
        cmd: str,
        args: str,
        arg_name: str = "",
        env: str = "",
        new_version_fn=lambda x: x,
        s3=False,
        do_second_apps=True,
        **eargs,
    ):
        self.lang = lang
        self.name = name
        self.raw_cmd = cmd
        self.cmd = new_version_fn(cmd)
        self.args = args
        self.stop_count = 2 if lang == "java" else 1
        self.arg_name = arg_name
        self.env = env
        self.s3 = s3
        self.do_second_apps = do_second_apps

    def id(self):
        if self.arg_name:
            return f"{self.lang}_{self.name}_{self.arg_name}"
        else:
            return f"{self.lang}_{self.name}"

    def __repr__(self):
        return f"{self.name}: lang={self.lang}, id={self.id()}" + (
            f" arg_name={self.arg_name}" if self.arg_name else ""
        )

    def _env(self):
        return f"-E {self.env}" if self.env else ""


def compile_tests(test_list):
    name_regex = re.compile(ARGS.name_filter) if ARGS.name_filter else None
    lang_regex = re.compile(ARGS.lang_filter) if ARGS.lang_filter else None

    def name_filter(test) -> bool:
        return name_regex.search(test.id()) if name_regex else True

    def lang_filter(test) -> bool:
        return lang_regex.search(test.lang) if lang_regex else True

    def combined_filter(test):
        return name_filter(test) and lang_filter(test)

    tests = list(filter(combined_filter, test_list))

    assert len(tests) > 0, "No tests to run!"

    return tests
