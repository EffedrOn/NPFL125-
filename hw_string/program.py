#!/usr/bin/env python3
import sys
import os
import regex as re
from collections import Counter

# Helper function to write contents to a file
def write_to_file(contents, task_number, file_name, script_dir):
    #name_of_file = f"{file_name}.{task_number}"
    # iam not sure where to save the result files 
    
    base_name = os.path.basename(file_name)
    name_of_file = os.path.join(script_dir, f"{base_name}.{task_number}")
    with open(name_of_file, "w") as outputfile:
        #print(contents, file=outputfile)
        outputfile.write(contents) # alternative way to write to a file


def sub_spaces(contents):
    """Print out the text with spaces substituted by underscores."""
    subsituted = re.sub(" ","_",contents)
    return subsituted

def only_all_uppercase_lines(contents):
    """Find and print only lines on which all letters are uppercase (such as "HELLO WORLD!")."""
    lines = contents.split("\n")
    filtered_lines = [line for line in lines if line and line.isupper()]

    return "\n".join(filtered_lines)

def word_per_line(contents):
    """
    Split the text into words.  maybe splitting on whitespace and punctuation
    Print out the result one word per line -- i.e. print the whole text (only missing
    the characters that you remove during the splitting), with words in the same order 
    as in the input file, but put newlines between words.
    """
    words = re.split(r"[^\w]+", contents) # split on everything else than word character 
    # iam not sure if thats correct should "hello-world" be 2 words???
    return "\n".join(word for word in words if word)


def words_subsequent_wowels(contents):
    """
    Find words containing at least two subsequent vowels. Print them out
    one word per line (all occurences, in the order in which they occur in
    the text; i.e. do not reorder the words in any way).
    """
    words = re.split(r"[^\w]+", contents)
    filtered_words = [word for word in words if word and re.search(r"[aeiouyAEIOUY]{2,}", word)]

    return "\n".join(filtered_words)

def remove_stopwords(contents):
    """
    Remove "stop words" from the text. Approximate the list of stop words by the list of words that have
    at least 10 occurrences in the text, independent of casing. Print the text (with stopwords removed), 
    one word per line.
    """
    words = re.split(r"[^\w]+", contents)
    frequency_list = Counter(word.lower() for word in words if word)
    stopwords = [word for word in frequency_list if frequency_list[word] >= 10]

    without_stopwords = [word for word in words if word and word.lower() not in stopwords]

    return "\n".join(without_stopwords)

# Helper function to convert integers to Roman numerals
def convert_int_to_roman(n):
    """Converts an integer (1-2000) to Roman numeral."""
    # 0 does not exist in Roman numerals
    if n <= 0 or n > 2000:
        return str(n)  # returning original 
    
    values = [
        (1000, 'M'),
        (900, 'CM'),
        (500, 'D'),
        (400, 'CD'),
        (100, 'C'),
        (90, 'XC'),
        (50, 'L'),
        (40, 'XL'),
        (10, 'X'),
        (9, 'IX'),
        (5, 'V'),
        (4, 'IV'),
        (1, 'I')
    ]
    
    result = []
    for value, numeral in values:
        count = n // value # how many times the value fits into n
        result.append(numeral * count)
        n %= value # remainder of the division
    
    return ''.join(result)

def replace_numbers_with_roman(contents):
    """
    Replace numbers by their Roman equivalents. It is sufficient to convert numbers up to 2000.
    Otherwise, leave the text exactly as it was, only replace the numbers. Print the whole text.
    """

    def replace_match(match):
        num_str = match.group(0)
        try:
            num = int(num_str)
            if 1<= num <= 2000:
                return convert_int_to_roman(num)
            else:
                return num_str
        except ValueError:
            return num_str
    
    result = re.sub(r'\b\d+\b', replace_match, contents) # matches whole numbers (word boundaries prevent matching digits inside words)
    return result

def join_and_reformat(contents):
    """
    Join the text into one line and reformat it so that each line (except for the last line) is at least
    40 characters long, but the line is wrapped at the first occasion after the 40th character. In other words,
    replace the first space after the 40th character with a newline. (But no line except the last line should be
    shorter than 40 characters.) You may need to add some spaces; e.g. if one line in the original text ends with
    the word "dog" and the next line starts with the word "cat", you obviously should not produce "dogcat" into the
    output... Print the whole text.
    """
    min_num_chars = 40
    one_line = contents.replace("\n", " ")
    one_line_splitted = one_line.split()

    result_lines = []
    current_line = ""
    for word in one_line_splitted:
        if current_line:
            potential_line = current_line + " " + word
        else:
            potential_line = word
        
        # If adding this word would make line >= 40, check if we should wrap
        if len(potential_line) >= min_num_chars:
            # If current_line is already >= 40, wrap now
            if len(current_line) >= min_num_chars:
                result_lines.append(current_line)
                current_line = word
            else:
                # Add the word to reach at least 40, then wrap
                current_line = potential_line
                result_lines.append(current_line)
                current_line = ""
        else:
            # Not long enough yet, keep adding
            current_line = potential_line
    
    # Print the last line 
    if current_line:
        result_lines.append(current_line)
    
    return "\n".join(result_lines)
def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename) as inputfile:
            contents = inputfile.read()
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        #1.
        result1 = sub_spaces(contents)
        write_to_file(result1, "1", filename, script_dir)
        
        #2.
        result2 = only_all_uppercase_lines(contents)
        write_to_file(result2, "2", filename, script_dir)
        
        #3.
        result3 = word_per_line(contents)
        write_to_file(result3, "3", filename, script_dir) 
        
        #4.
        result4 = words_subsequent_wowels(contents)
        write_to_file(result4, "4", filename, script_dir)
        
        #5.
        result5 = remove_stopwords(contents)
        write_to_file(result5, "5", filename, script_dir)
        
        #6.
        result6 = replace_numbers_with_roman(contents)
        write_to_file(result6, "6", filename, script_dir)
        
        #7
        result7 = join_and_reformat(contents)
        write_to_file(result7, "7", filename, script_dir)
    else:
        report = r"""
        In this tasks i switched between using regex and normal string operations. Iam more familiar with normal string operations therefore maybe somewhere
        it could seem somehow not optimal. I like the feature of regex to easily detect words with r"[^\w]+", which looks pretty short to me.
        I explicitly stated all the wowels as  aeiouyAEIOUY.
        I was little bit confused with stopwords definition as i didnnt quite understnd the aproximation of the list of stopwords.
        In roman numerals i took the approach to simply iterate over the roman alternative values and append the corresponding numeral to the result.
        I unfortunately did not implemented the tip about the unidecode for converting all characters into ACII :(.
        I tested the program with eng which worked as expected, aru (Mapudungun) which seemed pretty clean to me and chn
        (Chinese) which i was at first confused why result of task 5 has one symbol pre line but then i realised that symbol really 
        represents some kind of word :D. I was interested in the task 6 which will definitely not work for some other types of numbers.
        But in these 3 languages it worked as expected.
        """
        print(report)

if __name__  == "__main__":
    main()