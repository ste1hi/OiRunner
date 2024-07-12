# -*- coding: utf-8 -*-
import argparse
import json
import os
import sys

from .Exceptions import ProjectAlreadyExists, EnableHookError
from .util import HOOK_FILE_NAME


class OiRunner():

    def cmd_parse(self) -> None:
        '''Parse the command'''

        pa = argparse.ArgumentParser()
        sub_pa = pa.add_subparsers(dest="command")

        parser_make = sub_pa.add_parser("make", help="Create an OiRunner project.")
        parser_make.add_argument("name", type=str, help="Project name.")
        parser_make.add_argument("-q", "--questions", type=int, required=True, help="Number of questions.")
        parser_make.add_argument("-f", "--follow_question", action="store_true",
                                 help="Whether testing file's name is the same as question name.")
        parser_make.add_argument("-c", "--cpp", action="store_true", help="Whether create cpp file.")

        parser_sethook = sub_pa.add_parser("sethook", help="Enable hook file.")
        parser_sethook.add_argument("filename", type=str, choices=HOOK_FILE_NAME, help="The name of hook file.")
        self.args = pa.parse_args()
        if not self.args.command:
            pa.print_help()
            pa.error('The subcommand is required.')

    def _create_file(self, file: str) -> None:
        '''Creating file.'''
        open(file, "x").close()

    def make(self, name: str, questions: int, follow_question: bool, if_create_cpp_file: bool) -> None:
        '''
        Make a project in current directory.
        The `.OiRunner` directory will be created. In this directory, a `settings.json` file will be created.

        Args:
            name -- Project name.

            question -- Number of questions.

            follow_question -- Whether testing file's name is the same as question name.

            if_create_cpp_file -- Whether create cpp file.

        Raise:
            ProjectAlreadyExists -- Project already exists.
        '''

        if os.path.exists(".OiRunner"):
            raise ProjectAlreadyExists

        os.mkdir(".OiRunner")

        # Initialization settings。
        settings_path = os.path.join(".OiRunner", "settings.json")
        settings = {
            "name": name,
            "question_number": questions,
            "questions": {}
        }
        for question_number in range(1, questions + 1):
            os.mkdir(f"T{question_number}")
            os.chdir(f"T{question_number}")
            question_setting = {}

            if follow_question:
                self._create_file(f"T{question_number}.in")
                self._create_file(f"T{question_number}.out")
                self._create_file(f"T{question_number}.ans")

                question_setting[str(question_number)] = {
                    "id": question_number,
                    "name": f"T{question_number}",
                    "input_file": f"T{question_number}.in",
                    "output_file": f"T{question_number}.out",
                    "answer_file": f"T{question_number}.ans"
                }
            else:
                self._create_file("in.txt")
                self._create_file("out.txt")
                self._create_file("ans.txt")

                question_setting[str(question_number)] = {
                    "id": question_number,
                    "name": f"T{question_number}",
                    "input_file": "in.txt",
                    "output_file": "out.txt",
                    "answer_file": "ans.txt"
                }

            # Making files.
            if if_create_cpp_file:
                self._create_file(f"T{question_number}.cpp")
                question_setting[str(question_number)]["cpp"] = f"T{question_number}.cpp"
            settings["questions"] = question_setting
            os.chdir("..")  # Current directory is project's root directory.

            if not os.path.exists(os.path.join(".OiRunner", "hooks")):
                os.chdir(".OiRunner")
                os.mkdir("hooks")
                os.chdir("hooks")

                for hook_file in HOOK_FILE_NAME:
                    hook_file += ".bak"
                    self._create_file(hook_file)

                os.chdir(os.path.join("..", ".."))

        with open(settings_path, "w") as set:
            json.dump(settings, set)

    def sethook(self, filename: str) -> None:
        '''Enable hook file.'''
        file = filename + ".bak"  # Generated file name.
        if not os.path.exists(file):
            raise EnableHookError

        os.rename(file, filename)

    def run(self) -> None:
        '''
        The main function in oirunner command.

        Raise:
            SystemExit -- An error occurred.

            Exitcode `31` means this directory is already a project.

            Exitcode `32` means this directory already have existed some files.

            Exitcode `33` means hook file not exist.
        '''
        self.cmd_parse()
        try:
            if self.args.command == "make":
                self.make(self.args.name, self.args.questions, self.args.follow_question, self.args.cpp)
            elif self.args.command == "sethook":
                self.sethook(self.args.filename)
        except ProjectAlreadyExists:
            print("error:This directory is already a project.")
            sys.exit(31)
        except OSError:
            print("error:This directory already have existed some files.")
            sys.exit(32)
        except EnableHookError:
            print("error:Hook file not exist.")
            sys.exit(33)


def main():  # pragma: no cover
    oirunner = OiRunner()
    oirunner.run()
