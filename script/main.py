#!/usr/bin/env python3
if __name__ == "__main__":
    import os
    from side_functions import check_and_install, cli_input
    
    if "log.txt" not in os.listdir():
        check_and_install()
    
    input_file_path, wait_period, go_cutoff, gene_minimum, output_mode = cli_input()
    
    if input_file_path is not None:
        from run_functions import run_plaza, run_revigo, run_filters

        run_plaza(file_path=input_file_path, wait_period=wait_period)
        if output_mode == 2:
            run_revigo(wait_period=wait_period)
        else:
            run_revigo(wait_period=wait_period)
            run_filters(go_cutoff=go_cutoff, gene_minimum=gene_minimum)
