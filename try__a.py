import os, re
import zipfile
from model import Line, AutoCompleteData
from collections import defaultdict
import pickle
from runtime import timeit

from sortedcontainers import SortedList

import numpy as np

TOP_COUNT_CONST = 5
# FILE_NAME = '3_files.zip'
FILE_NAME = '2021-archive.zip'
fast_query_dict = {}
global_lines = []

@timeit
def main():
    namefile_list = []
    lines = []
    word_dict = defaultdict(SortedList)
    file_id = 0
    with zipfile.ZipFile(FILE_NAME) as z:
        for file_path in z.namelist():
            if not os.path.isdir(file_path):
                # read the file
                namefile_list += [file_path]
                line_number = 1
                with z.open(file_path) as f:
                    for line in f:
                        line_canonical_text = re.sub('[!@#$?,.]', '', line.decode("utf-8")).lower()
                        lines += [Line(file_number=file_id, line_number=line_number,
                                       original_text=line.decode("utf-8"),
                                       canonical_text=line_canonical_text,
                                       length=len(line_canonical_text))]
                        for word in line_canonical_text.split():
                            word_dict[word].add(len(lines) - 1)
                        line_number += 1
                file_id += 1


    with open('lines.pkl', 'wb') as pickle_file:
        pickle.dump(lines, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    with open('words_dict.pkl', 'wb') as pickle_file:
        pickle.dump(word_dict, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    with open('file_names.pkl', 'wb') as pickle_file:
        pickle.dump(namefile_list, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    print("done")


@timeit
def query(text: str):

    matched_lines = []
    canonical_text = re.sub('[!@#$?,.]', '', text).lower()

    list_sets = []
    for word in list(canonical_text.split()):
        list_sets += [set(word_dict[word])]
    matched_sentences_ids = set.intersection(*list_sets)

    for line_id in matched_sentences_ids:
        line = all_lines[line_id]
        if canonical_text in line.canonical_text:
            matched_lines += \
                [AutoCompleteData(completed_sentence=line.original_text,
                                  source_text=namefile_list[line.file_number],
                                  offset=line.canonical_text.index(canonical_text),
                                  score=len(text) * 2)]

        if len(matched_lines) == TOP_COUNT_CONST:
            break
    return matched_lines


@timeit
def find_match(text: str):
    existed_results = fast_query_dict.get(text)
    if existed_results:
        return existed_results
    fast_query_dict[text] = query(text)
    return fast_query_dict[text]


#main()
user_input = ''
with open('words_dict.pkl', 'rb') as pickle_load:
    word_dict = pickle.load(pickle_load)
with open('file_names.pkl', 'rb') as pickle_load:
    namefile_list = pickle.load(pickle_load)
with open('lines.pkl', 'rb') as pickle_load:
    all_lines = pickle.load(pickle_load)
while user_input != '#':
    user_input = input('Enter your text\n')
    count = 1
    ac_list = find_match(user_input)
    print(f"Here are {len(ac_list)} suggestions")
    for ac in ac_list:
        print(f'{count}. {ac.completed_sentence.strip()}')
        count += 1

