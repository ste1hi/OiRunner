# -*- coding: utf-8 -*-
import argparse
import json
import os
import sys

from .Exceptions import ProjectAlreadyExists


class OiRunner():

    def cmd_parse(self) -> None:
        pa = argparse.ArgumentParser()
        sub_pa = pa.add_subparsers(dest="command")

        parser_make = sub_pa.add_parser("make", help="Create an OiRunner project.")
        parser_make.add_argument("name", type=str, help="Project name.")
        parser_make.add_argument("-f", "--follow_project", action="store_true",
                                 help="Whether testing file's name is the same as project name.")
        parser_make.add_argument("-c", "--cpp", action="store_true", help="Whether create cpp file.")

        self.args = pa.parse_args()
        if not self.args.command:
            pa.print_help()
            pa.error('The subcommand is required.')

    def make(self, name: str, follow_project: bool, if_create_cpp_file: bool) -> None:
        if os.path.exists(".OiRunner"):
            raise ProjectAlreadyExists

        os.mkdir(".OiRunner")
        settings_path = os.path.join(".OiRunner", "settings.json")
        if if_create_cpp_file:
            open(f"{name}.cpp", "w").close()
        if follow_project:
            open(f"{name}.in", "w").close()
            open(f"{name}.out", "w").close()
            open(f"{name}.ans", "w").close()

            settings = {
                "name": name,
                "input_file": f"{name}.in",
                "output_file": f"{name}.out",
                "answer_file": f"{name}.ans"
            }
        else:
            open("in.txt", "w").close()
            open("out.txt", "w").close()
            open("ans.txt", "w").close()

            settings = {
                "name": name,
                "input_file": "in.txt",
                "output_file": "out.txt",
                "answer_file": "ans.txt"
            }

        with open(settings_path, "w") as set:
            json.dump(settings, set)

    def run(self) -> None:
        self.cmd_parse()
        try:
            if self.args.command == "make":
                self.make(self.args.name, self.args.follow_project, self.args.cpp)
        except ProjectAlreadyExists:
            print("error:There is already a project in this directory.")
            sys.exit()


def main():
    oirunner = OiRunner()
    oirunner.run()
