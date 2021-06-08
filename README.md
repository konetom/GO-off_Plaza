# GO-off with Plaza


This is a script for comfortable automation of Plaza v4.0 toolkit for Gene Ontology enrichment analysis (GOEA) with a query list of Arabidopsis thaliana gene IDs (TAIR10). <br>

Please check my Github page to find additional information: https://github.com/konetom/GO-off

<br>

Introduction
------------
The output from Plaza Dicots v4.0 GOEA is used as an input for REVIGO online tool which semantically reduces number of GO terms in the dataset (dispensability threshold default value is 0.7). <br>
Specific filters (for GO enrichment p-value and minumal number of genes associated with each GO term) can be applied to increase stringency in the final GO table.

<br>

Required software
-----------------
Mozilla Firefox (web browser), Python3.8+, UNIX/Linux or Windows OS

<br>

Required input file format
--------------------------
Single file in text format containing list of Arabidopsis gene IDs, each separated by a newline. <br>
If you don't have any data yet, you can use a file containing a list of gene IDs. <br>
The file can be found in the "input" folder of this GitHub repository.

<br>

Output files
------------
* Folder "output_date_time" (folder name including date and time to distinguish outputs):
    * Plaza GOEA raw output files are saved in "raw_plaza_downloads".
    * Plaza raw GOEA table (with associated genes) is saved in "without_filters"
    * Revigo reduced raw GO table is saved in "revigo_filters".
    * Final filtered GOEA table is saved in "with_filters".

<br>

Usage
-----
Download all files from "script" folder of this GitHub repository.
Open your console and locate the downloaded files.
Make sure you have installed Python version 3.8 or newer on your computer.
Run following line in your console to show help message:
<br>

<p align="center">
   <b>
python3 GO-off_Plaza.py -h
   </b>
</p>

    positional arguments:
    input               Input file (including relative or absolute path)

    optional arguments:
    -h, --help          show this help message and exit
    --timeout TIMEOUT   Maximum time (in seconds) given to each webpage to fully load {default: 300}

    --min_genes MIN_GENES
                        Filter for final filtered GO table. Minimum number of genes associated with GO {default: 3}

    --cutoff {0.05,0.01,0.001}
                        Filter for final filtered GO table. GO Enrichment p-value cutoff {default: 0.01}
                        options: 0.05, 0.01, 0.001

    --mode {1,2,3}      You can specify how many output files to generate {default: 3}
                        1: Only raw Plaza GOEA table (with associated genes, p-value filtered)
                        2: Plaza raw GOEA table (with associated genes) and raw Revigo reduced GO table
                        3: Both raw tables and the final filtered GOEA table (Revigo reduced, p-value filtered GO table with minimum number of associated genes).
<br>

Warnings
--------
Before running the script, there must be no empty experiment in your Plaza workbench named similarly to input file name (e.g. "Exp_[some_number]").
An error might show if the input file has more than 8000 gene IDs. This is not a sripting issue.

<br>

Notes
-----
You have to create an account in Plaza Dicots v4.0 prior running this script. Without login information, you cannot run the script. <br>
To avoid putting your login name and password each time of running the script, you can write and save your login name and login password in the "login.py" file. <br>
There you also define your special unique keyword, which you will be using instead of typing your login in console. <br>

<br>

Acknowledgment
-----
Please visit: https://bioinformatics.psb.ugent.be/plaza/pages/credits.
Also visit: https://github.com/konetom/GO-off
