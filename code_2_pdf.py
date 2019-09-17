#!/usr/bin/env python3

import re
import argparse
from pathlib import Path
from fpdf import FPDF

# TODO: make these configurable with input args
FILE_TYPES = ['/*/*.c', '*.h', 'README.md']
EXCLUDES_REG = [".*/build/.*"]

# string formats
# TODO: expand these to fill the margin of PDF either by inspection or setting a default value
FILENAME_HEADER = "\n\n" \
                  "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n" \
                  "  Filename: {}\n" \
                  "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"


def parse_args():
    parser = argparse.ArgumentParser("Converts git repo to pdf")
    parser.add_argument('-i', '--input', action='store', dest='input', required=True,
                        help='input dir of git repo')
    parser.add_argument('-o', '--output', action='store', dest='output', required=True,
                        help='output dir to save file')
    parser.add_argument('-t', '--text', action='store_true', dest='text',
                        help='generate a contents as an additional txt file')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # find files that match regex patterns in FILE_TYPES
    file_list = []
    for pattern in FILE_TYPES:
        for filename in Path(args.input).glob('**/{}'.format(pattern)):
            for exclude in EXCLUDES_REG:
                if re.match(exclude, "{}".format(filename)):
                    print("[WARNING] Skipping {} due to exclude rule: {}".format(filename, exclude))
                else:
                    print("[INFO] Adding {} to file_list".format(filename))
                    file_list.append(filename)

    # build pdf file
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # read contents into buffer
    output_lines = []
    for file in file_list:
        with open(file, 'r') as in_file:
            output_lines.append(FILENAME_HEADER.format(file))
            for line in in_file.readlines():
                output_lines.append(line)

    # write txt file if enabled
    if args.text:
        output_txt = "{}/output.txt".format(args.output)
        with open(output_txt, 'w') as f:
            f.writelines(output_lines)
        print("[INFO] Wrote repo contents to {}".format(output_txt))

    # build pdf and write file
    output_pdf = "{}/output.pdf".format(args.output)
    pdf.cell(0, 0, FILENAME_HEADER.format(file))
    for line in output_lines:
        pdf.cell(0, 0, line)
    pdf.output(output_pdf)
    print("[INFO] Wrote repo contents to {}".format(output_pdf))
