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

## Auto delete freopen command
Add `-f` of `--freopen` to enable auto delete `freopen` command.

> [!WARNING]
> This feature will modify your program file in disk. Use this flag carefully, though you have a backup file.

During modification, the backup file will be created in the same directory, named `<program file name>.bak`.

This feature only support the freopen function call that is directly written in the `main()`.

The form like below is supported:
```c++
freopen
    ("file name" , "r" , stdin),  // Supports line breaks and blanks.

freopen("file name", "w", stdout);
```
The form like below is unsupported:
```c++
#define fre(file_name) freopen(file_name, "w", stdout) // Presented in a #define form.

void fre(char file_name){
    freopen(file_name, "w", stdout); // Nested function call.
}
```
When your code contains unsupported form, use `-f` flag might lead to unexpected outcomes.

When use this flag without `-j`, the package will modify your program file directly.With `-j`, the package will modify your program file after all test cases were passed.