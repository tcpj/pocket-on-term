#! /usr/bin/env python3
import os
import os.path
import configparser
import sys
import argparse
import pickle

from collections import OrderedDict

from pot.pocketapi.pocket import Pocket
from reader import Reader
from reader import Article


CONFIG_PATH = os.path.join(
    os.environ["HOME"], ".config", "pocket-on-term.conf")

STATE_FILE = os.path.join("/", "var", "tmp", "pot.state")


def load_state():
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, "rb") as f:
            return pickle.load(f)


def save_state(data):
    with open(STATE_FILE, "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def load_config():
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as config_file:
            config = configparser.ConfigParser()
            config.read_file(config_file)
            return config


def save_config(sec, opt, val):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    if not config.has_section(sec):
        config.add_section(sec)

    config.set(sec, opt, val)
    
    with open(CONFIG_PATH, "w") as config_file:
        config.write(config_file)    


class Command(object):

    def __init__(self, arguments=None, *args):
        self.parser = self.create_parser(arguments)
        self.ns = self.parser.parse_args(args)

    def __getitem__(self, item):
        return getattr(self.ns, item)

    def executor(self):
        res = self.exec()
        parsed = self.parse(res)
        self.print_result(parsed)

    def parse(self, res):
        pass

    def print_result(self, data):
        pass

    def create_parser(self, arguments):
        parser = argparse.ArgumentParser()
        for a in arguments:
            if isinstance(a, tuple):
                n, kw = a
                parser.add_argument(n, **kw)
            else:
                parser.add_argument(a)

        return parser


class Get(Command):

    arguments = [
        "state",
        "count",
        (
            "-o", {
                "dest": "offset",
                "default": 0
            }
        ),
        (
            "-s", {
                "dest": "sort",
                "default": "newest"
            }
        ),
        (
            "-f", {
                "dest": "favorite",
                "action": "store_const",
                "const": 1,
                "default": 0
            }
        ),
        (
            "-t", {
                "dest": "tag"
            }
        )
    ]

    def __init__(self, *args):
        super(Get, self).__init__(self.arguments, *args)

    def exec(self):
        q = vars(self.ns)
        p_cli = Pocket(config["pocket"])
        res = p_cli.get(q)

        return res

    def print_result(self, data):
        for i, a in enumerate(data):
            print("[{}] {}".format(i, a.title))

    def parse(self, res):
        data = res["list"]
        a_list = OrderedDict(
            sorted(
                data.items(),
                key=lambda k_v: k_v[1]["sort_id"]
            )
        )

        a_list = [
            Article(id, a["resolved_title"], a["resolved_url"])
            for id, a in a_list.items()]

        save_state(a_list)
        return a_list


class Add(Command):

    arguments = ["url"]

    def __init__(self, *args):
        super(Add, self).__init__(self.arguments, *args)

    def exec(self):
        q = vars(self.ns)
        p_cli = Pocket(config["pocket"])
        res = p_cli.add(q)

        return res

    def print_result(self, data):
        print(data)

    def parse(self, res):
        if not res["status"]:
            return "Failed"
        return "OK - {}".format(res["item"]["title"])


class Read(Command):

    arguments = [
        ("id", {"type": int})]

    def __init__(self, *args):
        super(Read, self).__init__(self.arguments, *args)

    def exec(self):
        if state:
            article = state[self["id"]]
            Reader(
                article, 
                config["reader"] if config.has_section("reader") else None)


class Modify(Command):

    arguments = [
        ("id", {
            "type": int,
            "nargs": "*"
         })
    ]

    def __init__(self, action, *args):
        self.action = action
        super(Modify, self).__init__(self.arguments, *args)

    def exec(self):
        if not state:
            return

        ids = map(lambda x: state[x].id, self["id"])
        q = [{"action": self.action, "item_id": i} for i in ids]
        p_cli = Pocket(config["pocket"])
        res = p_cli.send(q)

        if not res:
            return False

        return res

    def parse(self, res):
        if not res["status"]:
            return "Failed"

        return "Success!"

    def print_result(self, data):
        print(data)


class Tag(Command):

    arguments = [
        "cmd",
        ("args", {"nargs": argparse.REMAINDER})
    ]

    class Common(Command):

        arguments = [
            ("ids", {
                "type": int,
                "nargs": "*"
            }),
            ("--tags", {
                "dest": "tags",
                "nargs": "*",
                "default": ""
            })
        ]

        def __init__(self, action, *args):
            self.action = action
            super(Tag.Common, self).__init__(self.arguments, *args)

        def exec(self):
            if not state:
                return

            ids = map(lambda x: state[x].id, self["ids"])
            q = [{
                "action": self.action,
                "tags": ",".join(self["tags"]),
                "item_id": i
            } for i in ids]

            p_cli = Pocket(config["pocket"])
            res = p_cli.send(q)

            return res

        def parse(self, res):
            if not res["status"]:
                return "Failed!"

            return "Success!"

        def print_result(self, data):
            print(data)

    class Clear(Command):

        arguments = [
            ("ids", {
                "type": int,
                "nargs": "*"
            })
        ]

        def __init__(self, *args):
            super(Tag.Clear, self).__init__(self.arguments, *args)

        def exec(self):
            if not state:
                return

            ids = map(lambda x: state[x].id, self["ids"])
            q = [{"action": "tags_clear", "item_id": i} for i in ids]
            p_cli = Pocket(config["pocket"])
            res = p_cli.send(q)

            return res

        def parse(self, res):
            if not res["status"]:
                return "Failed!"

            return "Success!"

        def print_result(self, data):
            print(data)

    def __init__(self, *args):
        super(Tag, self).__init__(self.arguments, *args)
        self.commands = {
            "add": (Tag.Common, "tags_add"),
            "remove": (Tag.Common, "tags_remove"),
            "replace": (Tag.Common, "tags_replace"),
            "clear": Tag.Clear
        }

    def exec(self):
        command = self.commands.get(self["cmd"])
        c_args = self["args"]
        if isinstance(command, tuple):
            command, opt = command
            self["args"].insert(0, opt)

        command(*c_args).executor()


class Set(Command):

    arguments = [
        "section",
        "option",
        "value"
    ]

    def __init__(self, *args):
        super(Set, self).__init__(self.arguments, *args)

    def exec(self):
        save_config(
            self["section"], self["option"], self["value"]) 


class Init(Command):

    def __init__(self):
        super(Init, self).__init__([])

    def exec(self):
        p_cli = Pocket(config["pocket"], redirect_uri=(
            "https://www.googledrive.com/host/"
            "0B3AlooTOdshyUi02M3V3UWVCdzA"))
        
        req_code = p_cli.get_request()
        link = (
            "https://getpocket.com/auth/authorize?"
            "request_token={}&redirect_uri={}").format(
                req_code, p_cli.redirect_uri)

        print("Allow access to your account at: {}".format(link))
        input()

        creds = p_cli.get_access(req_code)

        for o, v in creds.items():
            save_config("pocket", o, v)


if __name__ == "__main__":

    commands = {
        "set": Set,
        "init": Init,
        "get": Get,
        "add": Add,
        "read": Read,
        "archive": (Modify, "archive"),
        "readd": (Modify, "readd"),
        "favorite": (Modify, "favorite"),
        "unfavorite": (Modify, "unfavorite"),
        "delete": (Modify, "delete"),
        "tag": Tag
    }

    state = load_state()
    config = load_config()
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("cmd_args", nargs=argparse.REMAINDER)

    ns = parser.parse_args(sys.argv[1:])

    command = commands[ns.command]
    cmd_args = ns.cmd_args

    if isinstance(command, tuple):
        command, opt = command
        cmd_args.insert(0, opt)

    command(*cmd_args).executor()
