def cli_input():
    import argparse
    parser = argparse.ArgumentParser(description="GO-off with Plaza (by Ejave)", formatter_class=argparse.RawTextHelpFormatter, epilog="Script for automation of Plaza toolkit for Gene Ontology enrichment analysis on query list of gene IDs. \nPlease check my Github page to find additional information: https://github.com/konetom/GO-off_Plaza")
    parser.add_argument('input', type=str, help="Input file (including relative or absolute path)")
    parser.add_argument('--timeout', required=False, type=int, default=300, help="Maximum time (in seconds) given to each webpage to fully load {default: 300}\n ")
    parser.add_argument('--min_genes', required=False, type=int, default=3, help="Filter for final filtered GO table. Minimum number of genes associated with GO {default: 3}\n ")
    parser.add_argument('--cutoff', required=False, type=float, default=0.01, choices=[0.05, 0.01, 0.001], help="Filter for final filtered GO table. GO Enrichment p-value cutoff {default: 0.01}\noptions: 0.05, 0.01, 0.001\n ")
    parser.add_argument('--mode', required=False, type=int, default=3, choices=[1, 2, 3], help="You can specify how many output files to generate {default: 3}\n1: Only raw Plaza GOEA table (with associated genes) \n2: Plaza raw GOEA table (with associated genes) and raw Revigo reduced GO table \n3: Both raw tables and the final filtered GOEA table (Revigo reduced, p-value filtered GO table with minimum number of associated genes). \n")
    parser.add_argument('--output', type=str, help="Absolute path to the output directory")
    argparsed = parser.parse_args()
    returned = argparsed.input, argparsed.timeout, argparsed.cutoff, argparsed.min_genes, argparsed.mode, argparsed.output
    return returned


def opj(item1, item2):
    "Shorter way of joining paths."
    import os
    return os.path.join(item1, item2)


def check_and_install():
    """Pip is used to install packages needed for the rest of the code."""
    import subprocess
    import sys
    try:
        subprocess.check_call(['sudo', 'apt', 'install', 'python3-pip'])
    except Exception as e:
        print(e)
    pkg_list = ['pandas', 'lxml', 'xlrd', 'selenium', 'argparse', 'termcolor']
    installed = []
    for pkg in pkg_list:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])
            installed.append(pkg)
        except Exception as e:
            escape(e)
    return True if installed == pkg_list else False


def extra_modules():
    """Import required modules to run Firefox driver."""
    import os
    import pandas as pd
    from selenium import webdriver
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    if "log.txt" not in os.listdir():
        with open("log.txt", 'w') as f:
            f.write("Extra modules imported successfully.")
    return pd, webdriver, Select, WebDriverWait, By, EC


def drive_driver():
    """Run Firefox driver with adjusted profile."""
    import os
    import run_functions
    if "geckodriver.exe" in os.listdir(os.getcwd()):
        webdriver = extra_modules()[1]
        plaza_downloads_path = run_functions.plaza_downloads_path
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', "text/html")
        profile.set_preference('browser.download.dir', opj(os.getcwd(), plaza_downloads_path))
        driver = webdriver.Firefox(firefox_profile=profile, executable_path=opj(os.getcwd(), 'geckodriver.exe'))
        return driver
    else:
        escape("missing geckodriver in the directory")


def escape(*message):
    """Display message and quit."""
    import sys
    print(message)
    sys.exit()


def kill_banner(driver):
    """Check and remove banner from page."""
    import time
    time.sleep(0.5)
    if "Got it!" in driver.page_source:
        try:
            driver.find_element_by_link_text("Got it!").click()
        except:
            pass

def say_bye():
    from termcolor import colored as tc
    print(tc(r"""
..................................................
GO Enrichment Analysis is
                                               /|\
||==\\       _===_     ||\       ||  //=====   |||
||   \\    //     \\   ||\\      ||  ||        |||
||    ||  ||       ||  ||  \\    ||  ||        |||
||    ||  ||       ||  ||   \\   ||  ||====    |||
||   //   ||       ||  ||     \\ ||  ||        |||
||==//     \\_____//   ||       \||  \\=====   \|/
                                                O
..................................................
""", 'grey', 'on_green', attrs=['bold', 'blink']))
