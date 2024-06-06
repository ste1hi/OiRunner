# -*- coding: utf-8 -*-
import subprocess as sp
import argparse
import sys
import os
import re
import shutil
import time
from typing import Optional

from .submit import Submit


class Functions:

    def __init__(self) -> None:
        pass

    def _modify_file(self, file_name: str, file_type: str) -> int:
        '''
        Split the file into multiple files by line, with the output file located at ~tmp/.

        Args:
            file_name -- The name of input file.

            file_type -- The filename extension of input file.

        Returns:
            i -- Number of output files.

        Raise:
            SystemExit -- The file is empty.

            Exitcode `11` means some file is empty.
        '''
        i = 1
        a = ""
        flag = 0
        if not os.path.exists("~tmp"):
            os.mkdir("~tmp")
        with open(file_name, "r") as f:
            for line in f:
                file_path = os.path.join("~tmp", f"{i}.{file_type}")
                flag = 1
                if line.rstrip():
                    a += f"{line}"
                else:
                    if not a:
                        print(f"error:{file_name} is empty.")
                        shutil.rmtree("~tmp")
                        sys.exit(11)
                    with open(file_path, "w") as f:
                        f.write(a)
                    i += 1
                    a = ""
            if not flag:
                print(f"error:{file_name} is empty.")
                shutil.rmtree("~tmp")
                sys.exit(11)

        if a:
            file_path = os.path.join("~tmp", f"{i}.{file_type}")
            with open(file_path, "w") as f:
                f.write(a)
        return i

    def _output(self, num: int, opt_file: str) -> None:
        '''
        Merge and output the split files.

        Args:
            num -- The number of files to merge.

            opt_file -- Output file name.
        '''
        a = ""
        for file_num in range(1, num+1):
            a += f"#{file_num}:\n"
            out_file = os.path.join("~tmp", f"{file_num}.out")
            with open(out_file, "r") as f:
                for line in f:
                    a += f"{line}\n"

        with open(opt_file, "w") as out:
            out.write(a)

    def delete_freopen(self, path: str) -> None:
        '''
        Delete freopen command.

        Args:
            path -- The cpp file path.
        '''
        if not os.path.exists(path):
            raise ValueError("File not exists.")

        with open(path, "r") as file:
            content = file.read()

        back_file_path = os.path.join(os.path.dirname(path), os.path.basename(path) + ".bak")
        shutil.copy2(path, back_file_path)

        re_match = r'freopen(\s)*\((\s)*"(\w)*\.{0,1}(\w)*"(\s)*,(\s)*"\w"(\s)*,(\s)*std\w{2,3}(\s)*\)(\s)*[,|;]'
        changed_content = re.sub(re_match, "", content)

        with open(path, "w") as file:
            file.write(changed_content)


class BetterRunner:
    def __init__(self) -> None:
        self.input_file = "in.txt"
        self.output_file = "out.txt"
        self.answer_file = "ans.txt"
        self.func = Functions()

    def cmd_parse(self) -> None:
        '''Parse the command'''
        pa = argparse.ArgumentParser()
        pa.add_argument("filename", help="CPP file to be compiled (omitting '. cpp').")
        pa.add_argument("-n", "--name", default="a", help="Generate executable file name (omit '. exe').")
        pa.add_argument("-j", "--judge", action="store_true", help="Whether to evaluate.")
        pa.add_argument("-p", "--print", action="store_true", help="Whether to print details.")
        pa.add_argument("-if", "--inputfile", default="in.txt", help="Input file name.")
        pa.add_argument("-of", "--outputfile", default="out.txt", help="Output file name.")
        pa.add_argument("-af", "--answerfile", default="ans.txt", help="Answer file name.")
        pa.add_argument("-g", "--gdb", action="store_true", help="Whether to debug via gdb when the answer is incorrect.")
        pa.add_argument("-f", "--freopen", action="store_true", help="Add or delete freopen command.")
        pa.add_argument("-d", "--directgdb", action="store_true", help="Directly using gdb for debugging.")
        pa.add_argument("-r", "--remote", type=str, default=None, help="The question id in luogu.")
        pa.add_argument("-dO2", "--disabledO2", action="store_true", help="Disabled `O2` flag during remote judging.")
        pa.add_argument("-l", "--language", type=int, default=11,
                        help="The ID of the programming language used during remote judging.")
        pa.add_argument("--onlyinput", action="store_true", help="Using file input (invalid for - j).")
        pa.add_argument("--onlyoutput", action="store_true", help="Using file output (invalid when - j).")
        self.args = pa.parse_args()
        self.input_file = self.args.inputfile
        self.output_file = self.args.outputfile
        self.answer_file = self.args.answerfile
        if sys.platform == "linux":
            self.args.name = "./" + self.args.name + ".out"
        elif sys.platform == "win32":
            self.args.name = self.args.name + ".exe"

    def compile(self) -> None:
        '''
        Compile files and generate executable files.

        Raise:
            SystemExit -- Compilation failed.

            Exitcode `1` means compilation failed.
        '''
        try:
            compile = sp.Popen(["g++", self.args.filename + ".cpp", "-g", "-o", self.args.name])
            compile.wait()
            if compile.returncode == 0:
                print("Compilation successful.")
            else:
                print("Compilation failed.")
                sys.exit(1)

        # Can't sent Ctrl+c and get the messages.
        except KeyboardInterrupt:  # pragma: no cover
            print("\nManually exit, wish AC~(^ v ^)")
            sys.exit()

    def _check(self, opt_file: str, ipt_file: str, ans_file: str,
               file_num: int = 0, run_file: Optional[str] = None, if_print: Optional[bool] = None) -> bool:
        '''
        Local evaluation and get results.

        Args:
            opt_file -- Output file name.

            ipt_file -- Input file name.

            ans_file -- Answer file name.

            file_num -- File number.

            run_file -- Executable file name (None means use the value of the command line parameter).

            if_print -- Whether to output (None means use the value of the command line parameter).

        Return:
            if_pass -- Whether to pass the test.
        '''

        print(f"#{file_num}:")

        if run_file is None:
            run_file = self.args.name
        if if_print is None:
            if_print = self.args.print

        with open(opt_file, "w") as _out, open(ipt_file, "r") as _in:
            run = sp.Popen([run_file], stdin=_in, stdout=_out)

            ft = time.time()
            run.wait()
            now = time.time() - ft

            if run.returncode != 0:
                print(f"The return value is {run.returncode}. There may be issues with the program running.")

        with open(ans_file, "r") as ans, open(opt_file, "r") as my_ans:
            ans_list = [line.rstrip() for line in ans if line.rstrip()]
            my_ans_list = [line.rstrip() for line in my_ans if line.rstrip()]
            if ans_list == my_ans_list:
                if if_print:
                    print(f"Correct answer, takes {now:.5} seconds.")
                else:
                    print("Correct answer.")
                return True
            else:
                if if_print:
                    if len(ans_list) < 10:
                        print(f"Standard answer:{ans_list}\nYour answer:{my_ans_list}")
                    else:
                        print("The number of answer lines is too large.")
                    print("Wrong answer.")
                    print("Error data:")
                    with open(ipt_file, "r") as _in:
                        data_list = [line.rstrip() for line in _in if line.rstrip()]
                        data: str = ""
                        for data_line in data_list:
                            data += data_line
                            data += "\n"
                        if len(data) < 500:
                            print(data)
                        else:
                            print("The number of data words is too large.")
                else:
                    print("Wrong answer.")

                return False

    def run(self) -> None:
        '''Main function.'''
        try:
            if self.args.directgdb:
                gdb = sp.Popen(["gdb", self.args.name])
                gdb.wait()
                sys.exit()

            if not self.args.judge and self.args.freopen:
                self.func.delete_freopen(self.args.filename + ".cpp")

            if self.args.judge:
                flag = 0

                if os.path.exists("~tmp"):
                    shutil.rmtree("~tmp")
                self.func._modify_file(self.input_file, "in")
                i = self.func._modify_file(self.answer_file, "ans")

                for file_num in range(1, i + 1):
                    out_file = os.path.join("~tmp", f"{file_num}.out")
                    in_file = os.path.join("~tmp", f"{file_num}.in")
                    ans_file = os.path.join("~tmp", f"{file_num}.ans")
                    judge = self._check(out_file, in_file, ans_file, file_num)
                    if not judge:
                        flag += 1

                print(f"#final:Accuracy{((i - flag) / i): .2%}")
                self.func._output(i, self.output_file)
                shutil.rmtree("~tmp")

                if flag == 0 and self.args.freopen:
                    self.func.delete_freopen(self.args.filename + ".cpp")

                if flag == 0 and self.args.remote is not None:
                    print("\nSubmitting to remote judge.")
                    self.submit = Submit()
                    enableO2 = not self.args.disabledO2
                    rid = self.submit.upload_answer(self.args.remote, self.args.filename + ".cpp",
                                                    enableO2, self.args.language)
                    self.submit.get_record(rid, if_show_details=self.args.print)

                if self.args.gdb and flag > 0:
                    gdb = sp.Popen(["gdb", self.args.name])
                    gdb.wait()

            else:
                if self.args.onlyinput:
                    with open(self.input_file, "r") as _in:
                        print("The file has been executed.")
                        run = sp.Popen([self.args.name], stdin=_in)

                elif self.args.onlyoutput:
                    with open(self.output_file, "w") as _out:
                        run = sp.Popen([self.args.name], stdout=_out)

                else:
                    run = sp.Popen([self.args.name])

                run.wait()
                if run.returncode != 0:
                    print(f"The return value is {run.returncode}. There may be issues with the program running.")

                if self.args.remote is not None:
                    print("\nSubmitting to remote judge.")
                    self.submit = Submit()
                    enableO2 = not self.args.disabledO2
                    rid = self.submit.upload_answer(self.args.remote, self.args.filename + ".cpp",
                                                    enableO2, self.args.language)
                    self.submit.get_record(rid, if_show_details=self.args.print)

        # Can't sent Ctrl+c and get the messages.
        except KeyboardInterrupt:  # pragma: no cover
            if os.path.exists("~tmp"):
                shutil.rmtree("~tmp")
            print("\nManually exit, wish AC~(^ v ^)")


def main():
    runner = BetterRunner()
    runner.cmd_parse()
    runner.compile()
    runner.run()


if __name__ == "__main__":
    main()  # pragma: no cover
