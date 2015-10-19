#!/bin/bash
#
# 
#
echo "args: $@" 

ruby -e "require 'yaml'; YAML.load_file('$@')"