from nltk import RegexpTokenizer
import os
from pathlib import Path

from nltk.corpus import stopwords


def select_string_array_without_stop_words(string_array):
    english_stopwords = stopwords.words("english")
    return list(filter(lambda string: string not in english_stopwords, string_array))


def get_between_tokens(string, startToken, endToken, endOffset):
    return string[string.find(startToken) + len(startToken): string.find(endToken) - endOffset]


def select_doc_id(document):
    return get_between_tokens(document, 'NEWID="', '<DATE>', 3)


def select_tokenized_array(string):
    string_without_numbers = ''.join([i for i in string if not i.isdigit()])
    return RegexpTokenizer(r'\w+').tokenize(string_without_numbers)


def select_term_doc_id_pair(token, doc_id):
    return token, doc_id


def select_term_doc_id_list(token_array, doc_id):
    token_array_without_stop_words = select_string_array_without_stop_words(token_array)
    return list(map(lambda token: (token, doc_id), token_array_without_stop_words))


def select_formatted_term_doc_id_list(term_doc_id_list):
    occurrence_dictionary = {}
    for term_doc_id in term_doc_id_list:
        occurrence_dictionary[term_doc_id[0]] = "true"
    filtered_term_doc_id_list = filter(
        lambda local_term_doc_id: local_term_doc_id not in occurrence_dictionary, term_doc_id_list)
    filtered_term_doc_id_list = filter(lambda local_term_doc_id: len(local_term_doc_id[0]) > 1,
                                       filtered_term_doc_id_list)
    return sorted(filtered_term_doc_id_list)


def select_document_posting_list_from_term_doc_id_list(term_doc_id_list):
    posting_list = {}
    for term_doc_id in term_doc_id_list:
        posting_list[term_doc_id[0]] = term_doc_id[1]
    return posting_list


def select_document_posting_list_from_file_name(file_name):
    file_content = Path('reuters21578/' + file_name).read_text()
    tokenized_content = select_tokenized_array(file_content)
    term_doc_id_list = select_term_doc_id_list(tokenized_content, select_doc_id(file_content))
    formatted_term_doc_id_list = select_formatted_term_doc_id_list(term_doc_id_list)
    return select_document_posting_list_from_term_doc_id_list(formatted_term_doc_id_list)


def merge_posting_lists(global_posting_list, document_posting_list):
    for term, doc_id in document_posting_list.items():
        if term in global_posting_list:
            global_posting_list[term].append(doc_id)
        else:
            global_posting_list[term] = [doc_id]
    return global_posting_list


def select_global_posting_list():
    global_posting_list = {}
    for fileName in os.listdir("reuters21578")[:5]:
        document_posting_list = select_document_posting_list_from_file_name(fileName)
        global_posting_list = merge_posting_lists(global_posting_list, document_posting_list)
    return global_posting_list