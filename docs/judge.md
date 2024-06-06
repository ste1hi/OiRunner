# Judge program result

You can add `-j` or `--judge` flag to enable the judging feature. You can also add `-r` or `--remote` flag to judge your program on remote platform. [(see details)](./remotejudge.md)

## File directory structure
You need four files in your project directory.

```
<program file>.cpp
<input file>
<output file>
<answer file>
```

The default file names for `<input file>`,`<output file>` and `<answer file>` are `in.txt`, `out.txt` and `ans.txt`.

You can use `-if`, `-of` and `-af` or long argument `--inputfile`, `--outputfile` and `--answerfile` to change the file path and name.

For example:
```bash
oirun <program file> -if <input file path> -of <output file path> -af <answer file path> -j
```

## File content
### Input file
This file can contain more than one test cases. Each test case need to be divided by the blank line.

For example:
```
Case 1 input
Case 1 input

Case 2 input
Case 2 input
    ...
```
The input file must contain the same amount of test case in answer file.

### Answer file
In answer file you can divide the test case by blank line like input file.

For example:
```
Case 1 answer

Case 2 answer
```

## Run options

### -g or -- gdb
After enable this flag, the `gdb` will be started to debug program, when some test case is failed.

### -p or --print
Enable the print mode.

## Print mode
After enable the `print mode` , the more details during judgement will be shown.

When the test past, the time consumption will be given. But, the benchmark is python level, so it may be a little inaccurate.

When the test failed, the wrong answer and failed data will be shown. However due to the performance, some data will not be printed, when exceeding the maximum value.

| Item | Maximum quantity|
|-----|-----|
| answer lines | 9 |
| data character | 499 |