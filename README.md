autogenerate-config-docs
========================

Automatically generate configuration tables to document OpenStack.

Dependencies: python-git

This tool is divided into three parts:

1) Extraction of flags names


2) Grouping of flags
This is currently done manually, by using the flag name file and placing
a category after a space.

eg
$ head flagmappings/glance.flagmappings 
admin\_password registry
admin\_role api
admin\_tenant\_name registry
admin\_user registry
...

3) Creation of docbook-formatted configuration table files

eg
$ ./manipulate\_flags.py flagmappings/glance.flagmappings ~/temp/glance
