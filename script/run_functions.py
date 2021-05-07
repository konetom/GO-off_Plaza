import os
import sys
import re
import time
from shutil import rmtree, copy2
from distutils.dir_util import copy_tree
from side_functions import check_and_install, extra_modules, drive_driver, escape, opj, kill_banner

plaza_downloads_path, output_path = 'raw_plaza_downloads', 'output'
_wof, _wf, _rf = 'without_filters', 'with_filters', 'revigo_filters'
wof_path, wf_path, rf_path = opj(output_path, _wof), opj(output_path, _wf), opj(output_path, _rf)
pd, webdriver, Select, WebDriverWait, By, EC = extra_modules()


def run_plaza(file_path=None, wait_period=300):
    from getpass import getpass
    global _wof, _wf, _rf, plaza_downloads_path, output_path, wof_path, wf_path, rf_path
    global pd, webdriver, Select, WebDriverWait, By, EC, driver_wait
    
    plaza_url = 'https://bioinformatics.psb.ugent.be/plaza/versions/plaza_v4_dicots/workbench/logon'
    
    if '/' in file_path:
        input_path, file_name = file_path.rsplit('/', 1)[0], file_path.rsplit('/', 1)[-1]
    elif '\\' in file_path:
        input_path, file_name = file_path.rsplit('\\', 1)[0], file_path.rsplit('\\', 1)[-1]
    elif r'\\' in file_path:
        escape("Put valid path to your file.")
    else:
        file_name = file_path

    if plaza_downloads_path in os.listdir():
        rmtree(plaza_downloads_path)
        os.mkdir(plaza_downloads_path)
    else:
        os.mkdir(plaza_downloads_path)
    
    if output_path in os.listdir():
        rmtree(output_path)
    os.mkdir(output_path)
    os.mkdir(wof_path)
    os.mkdir(wf_path)
    os.mkdir(rf_path)
    
    if "login.py" in os.listdir():
        import login
        hidden_key = input("Key: ")
        if hidden_key == login.key:
            login_name = login.login_name
            login_password = login.login_password
        else:
            print("Incorrect key! Please enter your login manually.")
    else:
        login_name = input('Enter your username: ')
        login_password = getpass(prompt='Enter your password: ')

    # Login to Plaza Dicots v4.0:
    driver = drive_driver()
    driver_wait = WebDriverWait(driver, wait_period, poll_frequency=1)

    driver.get(url=plaza_url)
    driver.find_element_by_id("wb_login").send_keys(login_name)
    driver.find_element_by_id("wb_pass").send_keys(login_password)
    kill_banner(driver)
    try:
        driver_wait.until(EC.element_to_be_clickable((By.NAME, 'submit'))).click()
    except Exception as e:
        escape("Couldn't log in!", e)

    # Load and process input:
    full_name = file_name
    short_name = "Exp_" + "".join(re.findall(r"\d+", full_name[1:]))
    kill_banner(driver)
    kill_banner(driver)
    kill_banner(driver)
    if short_name in driver.page_source:
        kill_banner(driver)
        driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, short_name))).click()
    else:
        kill_banner(driver)
        driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[2]/div[2]/div[2]/form/div[2]/div[1]/div/input").send_keys(short_name)
        kill_banner(driver)
        driver_wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Create experiment']"))).click()
        kill_banner(driver)
        driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, short_name))).click()
        
        # Import data (gene IDs) to the experiment and map them to Ath:
        kill_banner(driver)
        driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Import using gene identifiers'))).click()
        kill_banner(driver)
        driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/form/input[3]'))).send_keys(str(opj(os.path.abspath(input_path), full_name)))
        driver_wait.until(EC.element_to_be_clickable((By.ID, "map_species_check"))).click()
        kill_banner(driver)
        Select(driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="map_species_select"]')))).select_by_visible_text('Arabidopsis thaliana')
        driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/form/input[5]'))).click()
        kill_banner(driver)
    
    # Run GOEA:
    kill_banner(driver)
    time.sleep(2)
    kill_banner(driver)
    try:
        driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, '... the GO enrichment.'))).click()
    except Exception:
        kill_banner(driver)
        try:
            driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/form/textarea'))).send_keys(open(opj(input_path, full_name), "r").readlines())
        except TimeoutError as e:
            escape(e)
        finally:
            kill_banner(driver)
            driver_wait.until(EC.element_to_be_clickable((By.ID, "map_species_check"))).click()
            kill_banner(driver)
            Select(driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="map_species_select"]')))).select_by_visible_text('Arabidopsis thaliana')
            kill_banner(driver)
            driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/form/input[5]'))).click()
            kill_banner(driver)
            try:
                driver_wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, '... the GO enrichment.'))).click()
            except Exception as e:
                escape("There was probably too many genes. Plaza could not handle that.", e)

    # Download GO enrichment/depletion data:
    kill_banner(driver)
    driver_wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div[1]/div[3]/form/input"))).click()
    kill_banner(driver)
    driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div[3]/div/a[1]'))).click()

    # Download GO associated genes (contining only the genes from input dataset):
    kill_banner(driver)
    driver_wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div[3]/div/a[2]'))).click()
    kill_banner(driver)
    driver_wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div/div/div/ul/li[3]/a"))).click()
    kill_banner(driver)
    driver_wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div/div/div/div/div[3]/div/div[1]/div[3]/form/input[3]"))).click()

    driver.quit()

    # Process GO tables
    listd = sorted(os.listdir(plaza_downloads_path))
    gene_file, go_file = listd[0], listd[1]
    
    genes_df = pd.read_table(opj(plaza_downloads_path, gene_file), index_col=None).iloc[:, [0, -3, -1]].rename(columns={'#go': 'GO IDs'})
    del genes_df['type']
    
    go_df = pd.read_table(opj(plaza_downloads_path, go_file), index_col=None).rename(columns={'GO-term': 'GO IDs'})
    go_df['Shown'] = go_df['Shown'].astype(str)
    go_df = go_df[go_df['Shown'] == 'True']
    del go_df['Shown']
    go_df = go_df[go_df['Log2-Enrichment'] > 0].sort_values(by=['Log2-Enrichment'], ascending=False)
    
    merge_with_genes = go_df.merge(genes_df, on='GO IDs')
    merge_with_genes['genes'] = [", ".join([j for j in sorted(i.split(','))]) for i in merge_with_genes['genes'].values]
    gene_lists = pd.DataFrame(([i.split(', ') for i in merge_with_genes['genes'].values]))
    concated = pd.concat([merge_with_genes, gene_lists], axis=1, ignore_index=False, sort=False)
    concated.to_excel(opj(wof_path, go_file.replace('.txt', '') + '(shown_true).xlsx'), index=None)


def run_revigo(wait_period=300):
    global _wof, _wf, _rf, plaza_downloads_path, output_path, wof_path, wf_path, rf_path
    global pd, webdriver, Select, WebDriverWait, By, EC

    driver = drive_driver()
    driver_wait = WebDriverWait(driver, wait_period, poll_frequency=1)

    file_without_filters = os.listdir(wof_path)[0]
    go_df = pd.read_excel(opj(wof_path, file_without_filters))
    for_revigo = go_df.loc[:, ['GO IDs', 'p-value']]

    if go_df.shape[0] != 0:
        driver.get('http://revigo.irb.hr/')
        if 'Accept and Close' in driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/button').text:
            driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/button').click()
    
        driver.find_element_by_xpath('//*[@id="ctl00_MasterContent_txtGOInput"]').send_keys(for_revigo.to_string(index=False, header=False).replace(' GO', 'GO').replace('  ', ' '))
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
            rev_df.to_excel(opj(rf_path, file_without_filters.replace(".xlsx", "_REVIGO.xlsx")), header=True, index=False)
    driver.quit()


def run_filters(go_cutoff=0.01, gene_minimum=3):
    global _wof, _wf, _rf, wof_path, wf_path, rf_path, pd
    
    rev_file = os.listdir(rf_path)[0]
    filterless_file = os.listdir(wof_path)[0]

    if rev_file.replace("_REVIGO", "") == filterless_file:
        r = pd.read_excel(opj(rf_path, rev_file))
        f = pd.read_excel(opj(wof_path, filterless_file))
        if f.shape[0] != 0:
            f = f[f['p-value'] < go_cutoff]
            f['column counts'] = f.notnull().sum(axis=1)
            f['gene list duplicated within table'] = f['genes'].duplicated().astype(str)
            f = f[(f['column counts'] > (6 + gene_minimum)) & (f['gene list duplicated within table'] == 'False')]
            del f['column counts']
            del f['gene list duplicated within table']
            if f.shape[0] != 0 and r.shape[0] != 0:
                result = f.merge(r, on='GO IDs')
                result = result.sort_values(by=['Log2-Enrichment', 'p-value'], ascending=[False, True])
                result = result.iloc[:, list(range(7)) + [-1]]
                del result['dispensability']
                result.to_excel(opj(wf_path, filterless_file.replace(".xlsx", "_filtered.xlsx")), index=None)
