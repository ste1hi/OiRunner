# -*- coding: utf-8 -*-
import subprocess as sp
import argparse
import sys
import os
import shutil
import time
from typing import Optional


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
        '''
        i = 1
        a = ""
        flag = 0
        if not os.path.exists("~tmp"):
            os.mkdir("~tmp")
        with open(file_name, "r") as f:
            for line in f:
                flag = 1
                if line.rstrip():
                    a += f"{line}"
                else:
                    if not a:
                        print(f"error:{file_name} is empty.")
                        shutil.rmtree("~tmp")
                        sys.exit()
                    with open(f"~tmp/{i}.{file_type}", "w") as _f:
                        _f.write(a)
                    i += 1
                    a = ""
            if not flag:
                print(f"error:{file_name} is empty.")
                shutil.rmtree("~tmp")
                sys.exit()

        if a:
            with open(f"~tmp/{i}.{file_type}", "w") as _f:
                _f.write(a)
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
            with open(f"~tmp/{file_num}.out", "r") as _f:
                for line in _f:
                    a += f"{line}"

        with open(opt_file, "w") as _out:
            _out.write(a)


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
        pa.add_argument("-p", "--print", action="store_true", help="Whether to print.")
        pa.add_argument("-if", "--inputfile", default="in.txt", help="Input file name.")
        pa.add_argument("-of", "--outputfile", default="out.txt", help="Output file name.")
        pa.add_argument("-af", "--answerfile", default="ans.txt", help="Answer file name.")
        pa.add_argument("-g", "--gdb", action="store_true", help="Whether to debug via gdb when the answer is incorrect.")
        pa.add_argument("-d", "--directgdb", action="store_true", help="Directly using gdb for debugging.")
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

        Raise：
        SystemExit -- Compilation failed.
        '''
        try:
            compile = sp.Popen(["g++", self.args.filename + ".cpp", "-g", "-o", self.args.name])
            compile.wait()
            if compile.returncode == 0:
                print("Compilation successful.")
            else:
                print("Compilation failed.")
                sys.exit()

        # Can't sent Ctrl+c and get the messages.
        except KeyboardInterrupt:  # pragma: no cover
            print("\nManually exit, wish AC~(^ v ^)")
            sys.exit()

    def _check(self, opt_file: str, ipt_file: str, ans_file: str,
               file_num: int = 0, run_file: Optional[str] = None, if_print: Optional[bool] = None) -> bool:
        '''
        Local evaluation and get results.

        Args：
        opt_file -- Output file name.

        ipt_file -- Input file name.

        ans_file -- Answer file name.

        file_num -- File number.
        run_file -- Executable file name (None means use the value of the command line parameter).
        if_print -- Whether to output (None means use the value of the command line parameter).

        Return：
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

            if self.args.judge:
                flag = 0

                if os.path.exists("~tmp"):
                    shutil.rmtree("~tmp")
                self.func._modify_file(self.input_file, "in")
                i = self.func._modify_file(self.answer_file, "ans")

                for file_num in range(1, i + 1):
                    judge = self._check(f"~tmp/{file_num}.out", f"~tmp/{file_num}.in", f"~tmp/{file_num}.ans",
                                        file_num)
                    if not judge:
                        flag += 1

                print(f"#final:Accuracy{((i - flag) / i): .2%}")
                self.func._output(i, self.output_file)
                shutil.rmtree("~tmp")

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
