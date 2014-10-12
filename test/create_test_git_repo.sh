#! /bin/bash

dir="$HOME/Desktop"
if [[ ! -z "$1" ]]; then
    dir="$1" 
fi

cd "$dir"
mkdir git_test
cd git_test

git init

# first commit
touch file1.txt
touch file2.txt
git add -A
git commit -m "initial commit"

# modify file1
echo "file1" > file1.txt
git commit -a -m "modified file1"

# add file3
touch file3.txt
git add -A
git commit -m "added file3"

# create a branch
git checkout -b add-directory
mkdir dir
cd dir
touch file4.txt
git add -A
git commit -m "added dir/file4.txt"

# switch back to master
cd ..
git checkout master

# create a README
touch README.md
echo "This is a test git repo. It's useful when I want to test a new git command." > README.md
git add -A
git commit -m "added README.md"
