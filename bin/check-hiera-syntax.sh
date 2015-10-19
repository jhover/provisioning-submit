#!/bin/bash
#
# 
#
echo "Checking YAML syntax in file: $@"

outfile=`mktemp`
 
ruby -e "require 'yaml'; YAML.load_file('$@')" > $outfile 2>&1
rc=$?
if [ $rc -eq 0 ]; then
 echo "File syntax is good."
else
 echo "File syntax is bad."
 er=`cat $outfile`
 echo "Error: $er"  
fi
rm -f $outfile