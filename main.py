import os, re
import zipfile
from model import Line, AutoCompleteData
import numpy as np
TOP_COUNT_CONST = 5
FILE_NAME = '2021-archive.zip'


def main():
    global lines
    global file_dict
    lines = []
    file_dict = {}
    file_id = 0
    with zipfile.ZipFile(FILE_NAME) as z:
        for file_path in z.namelist():
            if not os.path.isdir(file_path):
                # read the file
                file_dict[file_path] = file_id
                line_number = 1
                with z.open(file_path) as f:
                    for line in f:
                        lines += [Line(file_number=file_id, line_number=line_number,
                                       original_text=line.decode("utf-8"),
                                       canonical_text=re.sub('[!@#$?,.]', '', line.decode("utf-8")).lower())]
                    line_number += 1
                file_id += 1
    lines = list(sorted(lines, key=lambda l: (l.canonical_text, l.original_text)))
    print("done")


def query(text: str):
    matched_lines = []
    count = 0
    canonical_text = re.sub('[!@#$?,.]', '', text).lower()
    for line in lines:
        # get key by value
        key_list = list(file_dict.keys())
        val_list = list(file_dict.values())
        file_name = key_list[val_list.index(line.file_number)]
        #
        if canonical_text in line.canonical_text:
            matched_lines += [AutoCompleteData(completed_sentence=line.original_text,
                                               source_text=file_name,
                                               offset=line.canonical_text.index(canonical_text),
                                               score=len(text)*2)]
            count += 1
        if count == TOP_COUNT_CONST:
            break
    return matched_lines


main()
print(query("hello"))

