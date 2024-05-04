# Automatic operation

The package contain some automatic operation to make program running conveniently.

## Auto input
Add `--onlyinput` flag will enable this feature.

When this feature is enabled, the program will read the `inputfile`, get input content from this file and print through standard out.

The default input file is `in.txt`.You can change it by `--inputfile` flag. [See details](judge.md#file-directory-structure)

## Auto output
Add `--onlyoutput` flag will enable this feature.

When this feature is enabled, the program will get input from standard input store the output content in `outputfile`.

The default output file is `out.txt`.You can change it by `--outputfile` flag. [See details](judge.md#file-directory-structure)

## Auto gdb
Add `-d` or `--directgdb` will start gdb to debug the program directly.