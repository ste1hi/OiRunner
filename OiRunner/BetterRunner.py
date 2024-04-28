# -*- coding: utf-8 -*-
import subprocess as sp
import argparse
import sys
import os
import shutil
import time


class Functions:

    def __init__(self) -> None:
        pass

    def _modify_file(self, file_name: str, file_type: str) -> int:
        '''
        Split the file into multiple files by line, with the output file located at ~tmp/.

        参数：
        file_name -- 传入文件名
        file_type -- 输出文件扩展名

        返回值：
        i -- 输出文件数量

        可能异常：
        SystemExit -- 文件为空
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
                        print(f"error:{file_name}文件为空")
                        shutil.rmtree("~tmp")
                        sys.exit()
                    with open(f"~tmp/{i}.{file_type}", "w") as _f:
                        _f.write(a)
                    i += 1
                    a = ""
            if not flag:
                print(f"error:{file_name}文件为空")
                shutil.rmtree("~tmp")
                sys.exit()

        if a:
            with open(f"~tmp/{i}.{file_type}", "w") as _f:
                _f.write(a)
        return i

    def _output(self, num: int, opt_file: str) -> None:
        '''
        将分割后的文件合并输出。

        参数：
        num -- 要合并的文件数量。
        opt_file -- 输出文件名。
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
        '''
        命令行解析
        '''
        pa = argparse.ArgumentParser()
        pa.add_argument("filename", help="要编译的cpp文件(省略'.cpp')")
        pa.add_argument("-n", "--name", default="a", help="生成的可执行文件名(省略'.exe')")
        pa.add_argument("-j", "--judge", action="store_true", help="是否评测")
        pa.add_argument("-p", "--print", action="store_true", help="是否显示输出")
        pa.add_argument("-if", "--inputfile", default="in.txt", help="输入文件名")
        pa.add_argument("-of", "--outputfile", default="out.txt", help="输出文件名")
        pa.add_argument("-af", "--answerfile", default="ans.txt", help="答案文件名")
        pa.add_argument("-g", "--gdb", action="store_true", help="答案错误时是否使用gdb打开")
        pa.add_argument("--directgdb", action="store_true", help="直接使用gdb调试")
        pa.add_argument("--onlyinput", action="store_true", help="使用文件输入（-j时无效）")
        pa.add_argument("--onlyoutput", action="store_true", help="使用文件输出（-j时无效）")
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
        编译文件，生成可执行文件。

        可能异常：
        SystemExit -- 编译失败
        '''
        try:
            compile = sp.Popen(["g++", self.args.filename + ".cpp", "-g", "-o", self.args.name])
            compile.wait()
            if compile.returncode == 0:
                print("编译成功")
            else:
                print("编译失败")
                sys.exit()

        # Can't sent Ctrl+c and get the messages.
        except KeyboardInterrupt:  # pragma: no cover
            print("\n手动退出，祝AC~(^v^)")
            sys.exit()

    def _check(self, opt_file: str, ipt_file: str, ans_file: str,
               file_num: int = 0, run_file: str | None = None, if_print: bool | None = None) -> bool:
        '''
        本地评测，并获取结果。

        参数：
        opt_file -- 输出文件名
        ipt_file -- 输入文件名
        ans_file -- 答案文件名
        file_num -- 文件编号
        run_file -- 可执行文件名（None为使用命令行参数值）
        if_print -- 是否输出（None为使用命令行参数值）

        返回值：
        if_pass -- 测试是否通过
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
                print(f"返回值为{run.returncode}，程序运行可能有问题")

        with open(ans_file, "r") as ans, open(opt_file, "r") as my_ans:
            ans_list = [line.rstrip() for line in ans if line.rstrip()]
            my_ans_list = [line.rstrip() for line in my_ans if line.rstrip()]
            if ans_list == my_ans_list:
                if if_print:
                    print(f"答案正确，用时{now:.5}")
                else:
                    print("答案正确")
                return True
            else:
                if if_print:
                    if len(ans_list) < 10:
                        print(f"标准答案：{ans_list}\n实际答案：{my_ans_list}")
                    else:
                        print("答案行数过大")
                    print("答案错误")
                    print("错误数据：")
                    with open(ipt_file, "r") as _in:
                        data_list = [line.rstrip() for line in _in if line.rstrip()]
                        data: str = ""
                        for data_line in data_list:
                            data += data_line
                            data += "\n"
                        if len(data) < 500:
                            print(data)
                        else:
                            print("数据字数过多")
                else:
                    print("答案错误")

                return False

    def run(self) -> None:
        '''程序运行主函数'''
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

                print(f"#final:正确率{((i - flag) / i): .2%}")
                self.func._output(i, self.output_file)
                shutil.rmtree("~tmp")

                if self.args.gdb and flag > 0:
                    gdb = sp.Popen(["gdb", self.args.name])
                    gdb.wait()

            else:
                if self.args.onlyinput:
                    with open(self.input_file, "r") as _in:
                        print("文件已执行")
                        run = sp.Popen([self.args.name], stdin=_in)

                elif self.args.onlyoutput:
                    with open(self.output_file, "w") as _out:
                        run = sp.Popen([self.args.name], stdout=_out)

                else:
                    run = sp.Popen([self.args.name])

                run.wait()
                if run.returncode != 0:
                    print(f"返回值为{run.returncode}，程序运行可能有问题")

        except KeyboardInterrupt:
            if os.path.exists("~tmp"):
                shutil.rmtree("~tmp")
            print("\n手动退出，祝AC~(^v^)")


def main():
    runner = BetterRunner()
    runner.cmd_parse()
    runner.compile()
    runner.run()


if __name__ == "__main__":
    main()
