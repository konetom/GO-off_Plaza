"""Script for automation of Plaza toolkit for Gene Ontology enrichment analysis on query list of gene IDs.

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
    To avoid putting login name and password each time of script running, save login name and password in the "login.py file and define special keyword, that will be used instead of login.
"""

import os
import sys
import re
import time
import pandas as pd
from shutil import rmtree, copy2
from distutils.dir_util import copy_tree
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def escape(*message):
    """Display message and quit."""
    print(message)
    sys.exit()


def kill_banner():
    """Delete the banner. Not deleting it would make issues in next steps."""
    global driver
    if "Got it!" in driver.page_source:
        try:
            driver.find_element_by_link_text("Got it!").click()
        except Exception:
            pass
        finally:
            time.sleep(1)


if __name__ == "__main__":
    hidden_key = input("Key: ")
    wait_period = 300  # maximum time in seconds given to each webpage to load
    go_cutoff = 0.01
    temp_path = '..\\plaza_temp'
    script_path = '..\\script'
    input_path = '..\\input'
    plaza_download_path = '..\\plaza_downloads'
    output_path = '..\\_output'
    wof = '\\without_filters'
    wf = '\\with_filters'
    rf = '\\revigo_filters'
    if "_output" in os.listdir(".."):
        rmtree(output_path)
        os.mkdir(output_path)
        os.mkdir(output_path+wof)
        os.mkdir(output_path+wf)
        os.mkdir(output_path+rf)
    else:
        os.mkdir(output_path)
        os.mkdir(output_path+wof)
        os.mkdir(output_path+wf)
        os.mkdir(output_path+rf)
    try:
        if "login.py" in os.listdir(script_path):
            import login
    except Exception as e:
        escape(e)
    if "plaza_temp" in os.listdir(".."):
        rmtree(temp_path)
        os.mkdir(temp_path)
    else:
        os.mkdir(temp_path)
    if "plaza_downloads" in os.listdir(".."):
        rmtree(plaza_download_path)
        os.mkdir(plaza_download_path)
    else:
        os.mkdir(plaza_download_path)
    # geckodriver needs to be in the same folder as the script to run driver
    if "geckodriver.exe" not in os.listdir(script_path):
        escape("missing geckodriver in the directory")
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', "text/html")
    profile.set_preference('browser.download.dir', os.getcwd()+"\\"+temp_path)
    driver = webdriver.Firefox(firefox_profile=profile, executable_path=script_path+r'\geckodriver.exe')
    driver_wait = WebDriverWait(driver, wait_period, poll_frequency=1)
    driver.get('https://bioinformatics.psb.ugent.be/plaza/versions/plaza_v4_dicots/workbench/logon')
    # Login to Plaza with account name and password saved in file called login.py
    if hidden_key == login.key:
        driver.find_element_by_id("wb_login").send_keys(login.login_name)
        driver.find_element_by_id("wb_pass").send_keys(login.login_password)
    else:
        login_name = getpass(prompt='Enter your username: ')
        login_password = getpass(prompt='Enter your password: ')
        driver.find_element_by_id("wb_login").send_keys(login_name)
        driver.find_element_by_id("wb_pass").send_keys(login_password)
    try:
        driver_wait.until(EC.element_to_be_clickable((By.NAME, 'submit'))).click()
        kill_banner()
    except Exception as e:
        escape('Something went wrong!', e)
    # Load inputs
    try:
        listd = sorted(os.listdir(input_path))
        files = [i for i in listd if '.txt' in i]
    except Exception as e:
        escape(e)
    # Process inputs
    for n, file in enumerate(files):
        full_name = file
        short_name = "Exp_"+"".join(re.findall(r'\d+', full_name[1:]))
        kill_banner()
        if short_name in driver.page_source:
            driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, short_name))).click()
        else:
            kill_banner()
            driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[2]/div[2]/div[2]/form/div[2]/div[1]/div/input").send_keys(short_name)
            driver_wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Create experiment']"))).click()
            kill_banner()
            driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, short_name))).click()
            # Import data (gene IDs) to the experiment and map them to Ath
            kill_banner()
            driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Import using gene identifiers'))).click()
            driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/form/input[3]'))).send_keys(str(input_path+full_name))
            kill_banner()
            driver_wait.until(EC.element_to_be_clickable((By.ID, "map_species_check"))).click()
            Select(driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="map_species_select"]')))).select_by_visible_text('Arabidopsis thaliana')
            kill_banner()
            driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/form/input[5]'))).click()
        # Run GOEA in Plaza
        kill_banner()
        try:
            driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, '... the GO enrichment.'))).click()
        except Exception as e:
            try:
                driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/form/textarea'))).send_keys(open(input_path+"\\"+full_name, "r").readlines())
            except TimeoutError:
                escape(e)
            finally:
                kill_banner()
                driver_wait.until(EC.element_to_be_clickable((By.ID, "map_species_check"))).click()
                Select(driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="map_species_select"]')))).select_by_visible_text('Arabidopsis thaliana')
                kill_banner()
                driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/form/input[5]'))).click()
                try:
                    kill_banner()
                    driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, '... the GO enrichment.'))).click()
                except Exception as e:
                    escape("There was probably too many genes. Plaza could not handle that.", e)
        # NOTE: Set GO cutoff in the webpage (this step seems to me is not reliable, thus I will apply this filter on the final filtered datasets instead)
        # Compute and download GO enrichment/depletion data:
        kill_banner()
        driver_wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div[1]/div[3]/form/input"))).click()
        kill_banner()
        driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Download GO enrichment/depletion data'))).click()
        for i in os.listdir(temp_path):
            if str(i).startswith('go_enrichment'):
                copy2(temp_path+"\\"+i, temp_path+"\\"+str(n)+"_"+i)
                os.remove(temp_path+"\\"+i)
        # Download GO associated genes (only genes from input dataset)
        kill_banner()
        driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Download GO data'))).click()
        kill_banner()
        driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Functional Annotation'))).click()
        kill_banner()
        driver_wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Download GO data (3)']"))).click()
        # Proceed to next file, if there is some remaining
        if file != files[-1]:
            driver.get('https://bioinformatics.psb.ugent.be/plaza/versions/plaza_v4_dicots/workbench/experiments')
            kill_banner()
        else:
            copy_tree(temp_path, plaza_download_path)
    rmtree(temp_path)
    if "go_data.txt" in os.listdir(plaza_download_path):
        copy2(plaza_download_path+"\\go_data.txt", plaza_download_path+"\\go_data(0).txt")
        os.remove(plaza_download_path+"\\go_data.txt")
    listd = sorted(os.listdir(plaza_download_path))
    enrichs, go_datas = listd[:int(len(listd)/2)], listd[int(len(listd)/2):]
    for gene_file, go_file in zip(go_datas, enrichs):
        genes_df = pd.read_table(plaza_download_path+"\\"+gene_file, index_col=None).iloc[:, [0, -3, -1]].rename(columns={'#go': 'GO IDs'})
        # genes_df = genes_df[(genes_df['type'] == 'BP') | (genes_df['type'] == 'MF')]
        del genes_df['type']
        go_df = pd.read_table(plaza_download_path+"\\"+go_file, index_col=None).rename(columns={'GO-term': 'GO IDs'})
        go_df['Shown'] = go_df['Shown'].astype(str)
        go_df = go_df[go_df['Shown'] == 'True']
        del go_df['Shown']
        go_df = go_df[go_df['Log2-Enrichment'] > 0].sort_values(by=['Log2-Enrichment'], ascending=False)
        merge_with_genes = go_df.merge(genes_df, on='GO IDs')
        merge_with_genes['genes'] = [", ".join([j for j in sorted(i.split(','))]) for i in merge_with_genes['genes'].values]
        gene_lists = pd.DataFrame(([i.split(', ') for i in merge_with_genes['genes'].values]))
        concated = pd.concat([merge_with_genes, gene_lists], axis=1, ignore_index=False, sort=False)
        concated.to_excel(output_path+wof+"\\"+go_file.replace('.txt', '')+'(shown_true).xlsx', index=None)
    driver.get('http://revigo.irb.hr/')
    if 'Accept and Close' in driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/button').text:
        driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/button').click()
    for file_without_filters in os.listdir(output_path+wof):
        go_df = pd.read_excel(output_path+wof+"\\"+file_without_filters)
        if go_df.shape[0] != 0:
            for_revigo = go_df.loc[:, ['GO IDs', 'p-value']]
            driver.find_element_by_xpath('//*[@id="ctl00_MasterContent_txtGOInput"]').send_keys(for_revigo.to_string(index=False, header=False))
            dbase = driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_MasterContent_lstSpecies"]')))
            Select(dbase).select_by_visible_text('Arabidopsis thaliana')
            driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_MasterContent_btnStart"]'))).click()
            driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-id-1"]')))
            if "Biological Process" in driver.find_element_by_xpath('//*[@id="ui-id-1"]').text:
                driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-id-1"]'))).click()
                time.sleep(2)
                get_table = pd.read_html(driver.find_element_by_xpath('//*[@id="ctl00_MasterContent_dgBPTable"]').get_attribute('outerHTML'))[0]
                rev_df_1 = pd.DataFrame({'GO IDs': get_table.iloc[2:, 0], 'dispensability': (get_table.iloc[2:, 6]).astype(float)})
                rev_df = rev_df_1.copy()
                if "Cellular Component" in driver.find_element_by_xpath('//*[@id="ui-id-2"]').text:
                    driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-id-2"]'))).click()
                    time.sleep(2)
                    get_table2 = pd.read_html(driver.find_element_by_xpath('//*[@id="ctl00_MasterContent_dgCCTable"]').get_attribute('outerHTML'))[0]
                    rev_df_2 = pd.DataFrame({'GO IDs': get_table2.iloc[2:, 0], 'dispensability': (get_table2.iloc[2:, 6]).astype(float)})
                    rev_df = pd.concat([rev_df, rev_df_2])
                    if "Molecular Function" in driver.find_element_by_xpath('//*[@id="ui-id-3"]').text:
                        driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-id-3"]'))).click()
                        time.sleep(2)
                        get_table3 = pd.read_html(driver.find_element_by_xpath('//*[@id="ctl00_MasterContent_dgMFTable"]').get_attribute('outerHTML'))[0]
                        rev_df_3 = pd.DataFrame({'GO IDs': get_table3.iloc[2:, 0], 'dispensability': (get_table3.iloc[2:, 6]).astype(float)})
                        rev_df = pd.concat([rev_df, rev_df_3])
            rev_df = rev_df[rev_df['dispensability'] < 0.7]
            rev_df.to_excel(output_path+rf+f'\\{file_without_filters.replace(".xlsx", "")}_REVIGO.xlsx', header=True, index=False)
            if file_without_filters != os.listdir(output_path+wof+"\\")[-1]:
                driver.get('http://revigo.irb.hr/')
    # last section: filter data based on Revigo reduced GO terms and some additional user defined filters (log2 enrichment, p-value, gene list identity, GO types)
    rev_listd = sorted(os.listdir(output_path+rf))
    filterless_listd = sorted(os.listdir(output_path+wof))
    for rev_file in rev_listd:
        for filterless_file in filterless_listd:
            if rev_file.replace("_REVIGO", "") == filterless_file:
                r = pd.read_excel(output_path+rf+"\\"+rev_file)
                f = pd.read_excel(output_path+wof+"\\"+filterless_file)
                f = f[f['p-value'] < go_cutoff]
                f['column counts'] = f.notnull().sum(axis=1)
                f['gene list duplicated within table'] = f['genes'].duplicated().astype(str)
                f = f[(f['column counts'] > 9) & (f['gene list duplicated within table'] == 'False')]
                del f['column counts']
                del f['gene list duplicated within table']
                if f.shape[0] != 0 and r.shape[0] != 0:
                    result = f.merge(r, on='GO IDs')
                    result = result[(result['#GO-type'] == 'BP') | (result['#GO-type'] == 'MF')]
                    result = result.sort_values(by=['Log2-Enrichment', 'p-value'], ascending=[False, True])
                    result = result.iloc[:, list(range(7))+[-1]]
                    result['same_enr'] = (result['Log2-Enrichment'] == result.iloc[0, 2]).astype(str)
                    if result['same_enr'].value_counts()['True'] > 10:
                        result = result[result['same_enr'] == 'True']
                    else:
                        result = result.iloc[:20, :-2]
                    result.to_excel(output_path+wf+"\\"+filterless_file, index=None)
    driver.quit()
