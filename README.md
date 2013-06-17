autogenerate-config-docs
========================

Automatically generate configuration tables to document OpenStack.


Dependencies: python-git (version: 0.3.2 RC1), oslo.config

Setting up your environment
---------------------------

Note: This tool is best run in a fresh VM environment, as running it
 requires installing the dependencies of the particular OpenStack
 product you are working with. Installing all of that on your normal
machine could leave you with a bunch of cruft!

First install git, python-git, and python-pip

    $ sudo apt-get install git python-git python-pip

then, checkout the repository you are working with:

    $ git clone https://github.com/openstack/nova.git

and the tool itself:

    $ git clone https://github.com/fifieldt/autogenerate-config-docs.git

Next, install oslo.config

    $ sudo pip install oslo.config

and finally, the dependencies for the product you are working with:

    $ sudo pip install -r nova/requirements.txt

Now you are ready to use the tool.


Using the tool
--------------

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
