autogenerate-config-docs
========================

Automatically generate configuration tables to document OpenStack.

Dependencies: python-git (version: 0.3.2 RC1)

This tool is divided into three parts:

1) Extraction of flags names
eg

$ ./autohelp.py --action create -i flagmappings/nova.flagmappings -o names --path /repos/nova

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

$ ./autohelp.py --action create -i flagmappings/nova.flagmappings -o docbook --path /repos/nova
