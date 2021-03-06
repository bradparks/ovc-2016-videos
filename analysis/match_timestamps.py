import nltk
from utils import words_from_file, prepare_tokens
import datetime
import time


def tokenize_line(line):
    words = nltk.word_tokenize(line)
    return prepare_tokens(words, stem=True)


def time_to_delta_seconds(time_str, start_time):
    time_obj = time.strptime(time_str, '%H:%M:%S')
    seconds = datetime.timedelta(hours=time_obj.tm_hour, minutes=time_obj.tm_min, seconds=time_obj.tm_sec).total_seconds()
    delta = int(seconds - start_time)
    return delta

# map words to timestamps in a dictionary
def map_terms_to_timestamps(lines):
    terms_to_timestamps = {}
    for line in lines:
        timestamp = line[0]
        tokens = line[1]
        for token in tokens:
            if token in terms_to_timestamps:
                if timestamp not in terms_to_timestamps[token]:
                    terms_to_timestamps[token].append(timestamp)
            else:
                terms_to_timestamps[token] = [timestamp]

    return terms_to_timestamps

def file_to_timestamp_dictionary(filename):
    with open(filename) as handle:
        lines = handle.readlines()

    lines = [line.rstrip('\n').split('\t') for line in lines]

    # get the first timestamp in the document
    start_time = time_to_delta_seconds(lines[0][0], 0)

    # convert timestamp to delta seconds, tokenize the line as individual words
    lines = [(time_to_delta_seconds(line[0], start_time), tokenize_line(line[1])) for line in lines]

    # filter out empty lines
    lines = [line for line in lines if line[1]]

    # print out max timestamp
    # print(max([line[0] for line in lines]))

    # map tokens to timestamps
    tokens_to_timestamps = map_terms_to_timestamps(lines)

    # BIGRAMS
    # - both words on one line
    # OR
    # - last word of one line + first word of next line
    # ==> if we make a "line" = line + first word of next line, it should be good

    ## ORRR we already have it mapped to timestamp, list of tokens L
    # so we can change that to timestamp, (L[0][0] + L[0][1], ..., L[0][N] + L[1][0])
    bigram_lines = []
    num_lines = len(lines)
    for i, line in enumerate(lines):
        timestamp = line[0]
        tokens = line[1]

        bigrams = []
        num_tokens = len(tokens)
        for j, token in enumerate(tokens):
            if j + 1 < num_tokens:
                bigrams.append("{} {}".format(tokens[j], tokens[j + 1]))

        if i + 1 < num_lines and num_tokens > 0:
            next_line = lines[i + 1]
            next_line_tokens = next_line[1]
            bigrams.append("{} {}".format(tokens[num_tokens - 1], next_line_tokens[0]))

        bigram_lines.append((timestamp, bigrams))

    bigrams_to_timestamps = map_terms_to_timestamps(bigram_lines)

    # merge the timestamp dictionaries for both bigrams and individual word tokens
    terms_to_timestamps = {**tokens_to_timestamps, **bigrams_to_timestamps}

    return terms_to_timestamps




