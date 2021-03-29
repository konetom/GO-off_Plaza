# GO-off_Plaza

Script for automation of Plaza toolkit for Gene Ontology enrichment analysis on query list of gene IDs.

Introduction
------------
    The output GO sets are used as input in REVIGO online tool which semantically reduces number of GO terms in the dataset.
    Specific filters (for Log2 enrichment value, p-value and number of genes associated with each GO term) are applied to increase stringency in the final GO table.

Required software
-----------------
    Python3.8+, modules: "selenium", "pandas", "xmlx", "html5lib", "shutil", "distutils", "getpass"

Required input
--------------
    folder named "input" (inside should be one or more files, each containing query list of gene IDs) on same level as the folder "script"

Output files
------------
    Plaza GOEA output files are saved in folder "plaza_downloads".
    The processed tables are saved in folder "_output".
        Revigo output files are saved in "_output/revigo_filters".
        Final filtered GO tables are in folder "_output/with_filters".

Warnings
--------
    Before running the script, there must be no empty experiment in your Plaza workbench named similarly to input file names (e.g. "Exp_[numbers]").
    There might be issue if the input file has more than 8000 gene IDs. This can most probably be caused by Plaza, refusing the file import.

Notes
-----
    You have to own an active account in Plaza Dicots v4.0. Without it, you cannot run the script.
    To avoid putting login name and password each time of script running, save login name and password in the "login.py file and define special keyword, that will be used instead of login.

Acknowledgment
-----
Please visit: https://bioinformatics.psb.ugent.be/plaza/pages/credits.
    
Also check my previous script description, where you can find additional information: https://github.com/konetom/GO-off
