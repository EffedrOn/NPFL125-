from collections import Counter

# =======================================================
# =================== Tokens tasks ======================
# helper function to store results to files
def store_to_file_t(number, input):
    name_of_file = f"t{number}.txt"
    with open(name_of_file, "w") as outputfile:
        print(input, file=outputfile)

def count_chars(input_file):
    with open(input_file, "r") as f:
        content = f.read().rstrip('\n')
        number_of_chars = len(content)
    return number_of_chars

def split_into_tokens(input_file):
    with open(input_file, "r") as f:
        content = f.read().rstrip('\n')
        splitted = content.split()
    return splitted

def transform_to_token_per_line(tokens):
    return "\n".join(tokens)

def get_number_of_tokens(input_file):
    tokens = split_into_tokens(input_file)
    return len(tokens)

def print_first_three_chars_from_tokens(input_file):
    return " ".join(token[:3] for token in split_into_tokens(input_file))

def print_last_two_chars_from_first_20_tokens(input_file):
    return " ".join(token[-2:] for token in split_into_tokens(input_file)[:20])

def compute_avg_word_length(input_file):
    tokens = split_into_tokens(input_file)
    lengths_of_words = [len(word) for word in tokens]
    total = sum(lengths_of_words)
    avg = total / (get_number_of_tokens(input_file))
    return round(avg, 2)

#Create a frequency list of words and print out the most frequent word.
def get_most_frequent_word(input_file):
    # create a frequency list of words
    tokens = split_into_tokens(input_file)
    frequency_list = Counter(tokens)
    most_common = frequency_list.most_common(1)
    return most_common[0][0]

def get_most_frequent_char(input_file):
    with open(input_file, "r") as f:
        content = f.read().rstrip('\n')
    frequency_list = Counter(content)
    if ' ' in frequency_list:
        del frequency_list[' ']
    most_common = frequency_list.most_common(1)
    return most_common[0][0]

# =======================================================
# =================== Sentences tasks ===================
# helper function to store results to files
def store_to_file_s(number, input):
    name_of_file = f"s{number}.txt"
    with open(name_of_file, "w") as outputfile:
        print(input, file=outputfile)

# helper function to split content into sentences
def split_to_sentences(input_file):
    with open(input_file, "r") as f:
        content = f.read().rstrip('\n')
    sentences = [sentence.strip() for sentence in content.split(".")]
    sentences = [sentence for sentence in sentences if sentence] # removing any empty strings from sentences list
    return sentences

def transform_to_sentences_per_line(input_file):
    sentences = split_to_sentences(input_file)
    return "\n".join(sentences)

def get_sentences_count(input_file):
    sentences = split_to_sentences(input_file)
    return len(sentences)

def num_chars_in_sentences(input_file):
    sentences = split_to_sentences(input_file)
    counts = [str(len(sentence)) for sentence in sentences]
    return " ".join(counts)

def split_sentences_into_tokens(input_file):
    sentences = split_to_sentences(input_file)
    splitted = [sentence.split() for sentence in sentences]
    return(splitted)

def number_of_words_in_sentences(input_file):
    splitted_sentences = split_sentences_into_tokens(input_file)
    words_per_sentece = [len(splitted_to_words) for splitted_to_words in splitted_sentences]
    return " ".join(str(count) for count in words_per_sentece)

def average_sentence_word_length(input_file):
    splitted_sentences = split_sentences_into_tokens(input_file)
    words_per_sentece = [len(splitted_to_words) for splitted_to_words in splitted_sentences]
    total = sum(words_per_sentece)
    avg =  (total / len(words_per_sentece))
    return round(avg, 2)

def average_sentence_char_length(input_file):
    sentences = split_to_sentences(input_file)
    lengths = [len(sentence) for sentence in sentences]
    if not lengths:
        return 0.0
    avg = sum(lengths) / len(lengths)
    return round(avg,2)

def get_first_2_words_of_sentences(input_file):
    splitted_sentences = split_sentences_into_tokens(input_file)
    result_lines = []
    
    for sentence in splitted_sentences:
        first_2_words = sentence[0:2]
        result_lines.append(" ".join(first_2_words))
    return "\n".join(result_lines)

def first_char_of_2nd_word_3rd_sentence(input_file):
    sentences_tokens = split_sentences_into_tokens(input_file)
    third_sentence = sentences_tokens[2]
    second_word = third_sentence[1]
    return second_word[0]

def main():
    file_name = "genesis.txt"

    # Tokens tasks
    store_to_file_t(1, count_chars(file_name))
    store_to_file_t(2, transform_to_token_per_line(split_into_tokens("genesis.txt")[:20]))
    store_to_file_t(3, get_number_of_tokens("genesis.txt"))
    store_to_file_t(4, print_first_three_chars_from_tokens("genesis.txt"))
    store_to_file_t(5, print_last_two_chars_from_first_20_tokens("genesis.txt"))
    store_to_file_t(6, compute_avg_word_length("genesis.txt"))
    store_to_file_t(7, get_most_frequent_word("genesis.txt"))
    store_to_file_t(8, get_most_frequent_char("genesis.txt"))

    # Sentences tasks
    store_to_file_s(1, transform_to_sentences_per_line(file_name))
    store_to_file_s(2, get_sentences_count(file_name))
    store_to_file_s(3, num_chars_in_sentences(file_name))
    store_to_file_s(4, split_sentences_into_tokens(file_name))
    store_to_file_s(5, number_of_words_in_sentences(file_name))
    store_to_file_s(6, average_sentence_word_length(file_name))
    store_to_file_s(7, average_sentence_char_length(file_name))
    store_to_file_s(8, get_first_2_words_of_sentences(file_name))
    store_to_file_s(9, first_char_of_2nd_word_3rd_sentence(file_name))

    
if __name__ == "__main__":
    main()