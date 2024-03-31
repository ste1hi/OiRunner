import subprocess as sp
import argparse
import sys
import os
import shutil
import time


class BetterRunner:
    def __init__(self):
        pass

    def cmd_parse(self):
        '''
        命令行解析
        '''
        pa = argparse.ArgumentParser()
        pa.add_argument('filename', help="要编译的cpp文件(省略'.cpp')")
        pa.add_argument('-n', '--name', default="a", help="生成的可执行文件名(省略'.exe')")
        pa.add_argument('-j', '--judge', action='store_true', help="是否评测")
        # pa.add_argument('-u','--use_multiple_processes',action='store_true',help="是否使用多进程评测")
        pa.add_argument('-p', '--print', action='store_true', help="是否显示输出")
        pa.add_argument('-if', '--inputfile', default='in.txt', help="输入文件名")
        pa.add_argument('-of', '--outputfile', default='out.txt', help="输出文件名")
        pa.add_argument('-af', '--answerfile', default='ans.txt', help="答案文件名")
        pa.add_argument('-g', '--gdb', action='store_true', help="答案错误时是否使用gdb打开")
        pa.add_argument('-gf', '--gdbfile', default=None, help="gdb调试输入文件")
        pa.add_argument('--directgdb', action='store_true', help="直接使用gdb调试")
        pa.add_argument('--onlyinput', action='store_true', help="使用文件输入（-j时无效）")
        pa.add_argument('--onlyoutput', action='store_true', help="使用文件输出（-j时无效）")
        self.args = pa.parse_args()

        self.args.use_multiple_processes = False
        self.input_file = self.args.inputfile
        self.output_file = self.args.outputfile
        self.answer_file = self.args.answerfile
        if sys.platform == "linux":
            self.args.name = "./" + self.args.name + '.out'
        elif sys.platform == "win32":
            self.args.name = self.args.name + '.exe'

    def compile(self):
        '''
        编译文件
        '''
        try:
            compile = sp.Popen(['g++', self.args.filename + '.cpp', '-g', '-o', self.args.name])
            compile.wait()
            if compile.returncode == 0:
                print("编译成功")
            else:
                print("编译失败")
                exit(0)
        except KeyboardInterrupt:
            print("\n手动退出，祝AC~(^v^)")
            exit(0)

    def _modify_file(self, file_name, file_type):
        '''
        将文件按行分割
        '''
        i = 1
        a = ""
        if not os.path.exists('~tmp'):
            os.mkdir('~tmp')
        with open(file_name, "r") as f:
            for line in f:
                if line.rstrip():
                    a += f"{line}"
                else:
                    if not a:
                        print(f"error:{file_name}文件为空")
                        shutil.rmtree('~tmp')
                        exit(0)
                    with open(f"~tmp/{i}.{file_type}", "w") as _f:
                        _f.write(a)
                    i += 1
                    a = ""
        if a:
            with open(f"~tmp/{i}.{file_type}", "w") as _f:
                _f.write(a)
        return i

    def _output(self, num):
        '''
        将分割后的文件合并输出
        '''
        a = ""
        for file_num in range(1, num+1):
            a += f"#{file_num}:\n"
            with open(f"~tmp/{file_num}.out", "r") as _f:
                for line in _f:
                    a += f"{line}"

        with open(self.args.outputfile, "w") as _out:
            _out.write(a)

    def _check(self, opt_file, ipt_file, ans_file, file_num=0, run_file=None):
        '''
        本地评测
        '''

        print(f"#{file_num}:")

        if run_file is None:
            run_file = self.args.name

        with open(opt_file, "w") as _out, open(ipt_file, "r") as _in:
            run = sp.Popen([run_file], stdin=_in, stdout=_out)

            if not self.args.use_multiple_processes:
                ft = time.time()
                run.wait()
                now = time.time() - ft

            if run.returncode != 0:
                print(f"返回值为{run.returncode}，程序运行可能有问题")

        with open(ans_file, "r") as ans, open(opt_file, "r") as my_ans:
            ans = [line.rstrip() for line in ans if line.rstrip()]
            my_ans = [line.rstrip() for line in my_ans if line.rstrip()]
            if ans == my_ans:
                if self.args.print:
                    # print(f"标准答案：{ans}\n实际答案：{my_ans}")
                    print(f"答案正确，用时{now:.5}")
                else:
                    print("答案正确")
                return True
            else:
                if self.args.print:
                    # print(f"标准答案：{ans}\n实际答案：{my_ans}")
                    print("答案错误")
                    print("错误数据：")
                    with open(ipt_file, "r") as _in:
                        for line in _in:
                            if line.rstrip():
                                print(line.rstrip())
                else:
                    print("答案错误")

                return False

    def _copy_file(self, i):
        '''
        复制文件，为多进程评测准备
        '''
        for file_num in range(1, i + 1):
            dst = os.path.join(r'~tmp/', f"{file_num}_{self.args.name}")
            shutil.copy2(self.args.name, dst)

    def _debug(self):
        """
        使用gdb调试
        """
        if self.args.gdbfile is None:
            gdb = sp.Popen(['gdb', self.args.name])
            gdb.wait()
        else:
            with open(self.args.gdbfile, "r") as f:
                gdb = sp.Popen(['gdb', self.args.name], stdin=sp.PIPE, text=True)
                for line in f:
                    if line.rstrip():
                        line = str(line.rstrip()) + "\n"
                        # if line != "r":
                        #     line = line + "\n"
                        gdb.stdin.write(line)
                        gdb.stdin.flush()
                # print(gdb.stdout.read())
                # gdb.stdin.close()

                gdb.stdin = sys.stdin
                gdb.wait()

    def run(self):
        """
        程序主函数
        """
        try:
            if self.args.directgdb:
                self._debug()
                exit(0)

            if self.args.judge:
                flag = 0

                if os.path.exists('~tmp'):
                    shutil.rmtree('~tmp')
                self._modify_file(self.args.inputfile, "in")
                i = self._modify_file(self.args.answerfile, "ans")
                if self.args.use_multiple_processes:
                    self._copy_file(i)

                for file_num in range(1, i + 1):

                    if self.args.use_multiple_processes:
                        judge = self._check(f"~tmp/{file_num}.out", f"~tmp/{file_num}.in", f"~tmp/{file_num}.ans",
                                            file_num, f"~tmp/{file_num}_{self.args.name}")
                    else:
                        judge = self._check(f"~tmp/{file_num}.out", f"~tmp/{file_num}.in", f"~tmp/{file_num}.ans",
                                            file_num)

                    if not judge:
                        flag += 1

                print(f"#final:正确率{((i - flag) / i) : .2%}")
                self._output(i)
                shutil.rmtree('~tmp')

                if self.args.gdb and flag > 0:
                    self._debug()

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
            if os.path.exists('~tmp'):
                shutil.rmtree('~tmp')
            print("\n手动退出，祝AC~(^v^)")


def main():
    runner = BetterRunner()
    runner.cmd_parse()
    runner.compile()
    runner.run()


if __name__ == "__main__":
    main()
