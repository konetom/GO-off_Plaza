#!/usr/bin/env python3
import main


def cli_input():
    import argparse
    parser = argparse.ArgumentParser(description="GO-off_Plaza CLI")
    parser.add_argument('i', '--input_file', required=True, type=str, help="path to input file")
    parser.add_argument('t', 'page_timeout', requred=False, type=int, default=300, choices=range(600), help="maximum time in seconds given to each webpage to load")
    argparsed = parser.parse_args()

