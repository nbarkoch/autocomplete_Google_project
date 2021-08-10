import os, re
import zipfile
from model import Line, AutoCompleteData
import pickle

from runtime import timeit

TOP_COUNT_CONST = 5
FILE_NAME = '2021-archive.zip'
fast_query_dict = {}


@timeit
def main():
    lines = []
    namefile_list = []
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
                    line_number += 1
                file_id += 1
    lines = list(sorted(lines, key=lambda l: (l.canonical_text, l.original_text)))

    with open('lines.pkl', 'wb') as pickle_file:
        pickle.dump(lines, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    with open('file_names.pkl', 'wb') as pickle_file:
        pickle.dump(namefile_list, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    print("done")


@timeit
def query(text: str):
    matched_lines = []
    canonical_text = re.sub('[!@#$?,.]', '', text).lower()
    text_len = len(canonical_text)

    with open('lines.pkl', 'rb') as pickle_load:
        lines = pickle.load(pickle_load)

    with open('file_names.pkl', 'rb') as pickle_load:
        namefile_list = pickle.load(pickle_load)

    for line in lines:
        file_name = namefile_list[line.file_number]
        if text_len <= line.length and canonical_text in line.canonical_text:
            matched_lines += [AutoCompleteData(completed_sentence=line.original_text,
                                               source_text=file_name,
                                               offset=line.canonical_text.index(canonical_text),
                                               score=len(text)*2)]
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



# main()

# count = 1
# ac_list = find_match("this is")
# print(f"Here are {len(ac_list)} suggestions")
# for ac in ac_list:
#     print(f'{count}. {ac.completed_sentence}', end='')
#     count += 1


user_input = ''
while user_input != '#':
    user_input = input('Enter your text\n')
    count = 1
    ac_list = find_match(user_input)
    print(f"Here are {len(ac_list)} suggestions")
    for ac in ac_list:
        print(f'{count}. {ac.completed_sentence}', end='')
        count += 1