#!/usr/bin/env python3
"""
If tagger.py is run as script, it should expect one cmd line argument, the name of the training file.
It should train on that file and store the trained model under the name tagger.model :
    > tagger.py train.tsv
    -> storesa model train on the train.tsv file into tagger.model file

I need to use the name-main syntax, e.g:
if __name__=="__main__":
    tagger = Tagger()
    tagger.train(sys.argv[1])
    tagger.save('tagger.model')

"""

"""
Simple POS tagger implementation using only standard library
Trains by counting word->tag frequencies and using most common tag
"""

import sys
import pickle
from collections import defaultdict, Counter
import re

class Tagger:
    def __init__(self):
        self.model = {}  # Dictionary: word -> most common tag
        self.default_tag = 'N'  # Default tag for unknown words

    def train(self, filename):
        """
        Reads in a UTF-8 TSV file and learns a tagging model from it.
        format of the file is: 
           word[tab]pos 
           or an empty line for a sentence boundary
        the tagging model can be simply dictionary 
        """
        # Count all word->tag pairs
        word_tag_counts = defaultdict(Counter)
        all_tags = Counter()
        
        # Try UTF-8 first, then fall back to iso-8859-2
        encodings = ['utf-8', 'iso-8859-2', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    for line in f:
                        line = line.strip()
                        if line == '':
                            continue
                        
                        parts = line.split('\t')
                        if len(parts) == 2:
                            word = parts[0]
                            tag = parts[1].strip()
                            if tag:
                                word_tag_counts[word][tag] += 1
                                all_tags[tag] += 1
                    break  # Success, exit the encoding loop
            except (UnicodeDecodeError, Exception) as e:
                continue  # Try next encoding
        
        # Store most common tag for each word
        # this is the first primitive implementation for now
        for word, tag_counts in word_tag_counts.items():
            self.model[word] = tag_counts.most_common(1)[0][0]
        
        # Set default tag to most common tag overall
        if all_tags:
            self.default_tag = all_tags.most_common(1)[0][0]
 
            
    def save(self, filename):
        """
        saves the tagging model to a file using pickle
        """
        try:
            with open(filename, 'wb') as f:
                pickle.dump({'model': self.model, 'default_tag': self.default_tag}, f)
        except Exception as e:
            pass
            
    def load(self, filename):
        """
        loads the tagging model from a file
        """
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.model = data.get('model', {})
                self.default_tag = data.get('default_tag', 'N')
        except Exception as e:
            self.model = {}
            self.default_tag = 'N'
            
    def predict(self, word):
        """
        predicts and returns the POS tag for a given word
        must be a valid 1-letter POS tag for any word
        """
        # Return stored tag if word is known, otherwise default
        return self.model.get(word, self.default_tag)
        
    def predict_all(self, filename):
        """
        predicts POS tags for all words in a file
        the format of the file is one word per line, or an empty line for sentence boundary, UTF-8 encoding
        the output should be returned as a list of the POS labels, or an empty string for sentence boundary e.g. ['N', 'V', 'Z', '', 'R']
        """
        results = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line == '':
                        results.append('')
                    else:
                        results.append(self.predict(line))
        except Exception as e:
            pass
        return results
        

    def eval(self, filename):
        """
        reads in a UTF-8 TSV test file (word[tab]pos), predicts pos for all the words
        compares the predictions to the true labels, and returns the accuracy rounded to 2 decimal places.
        
        file also contains empty lines as sentences boundaries. (prediction on these should not be included into the evaluation score)
        therefore only compute the accuracy of predictions on non-empty lines

        the reported accuracy should be the microaverage, i.e percentage of words that got the correct label.(the sentence boundaries do not play any role here)
        """
        correct = 0
        total = 0
        
        # Try multiple encodings like in train()
        encodings = ['utf-8', 'iso-8859-2', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    for line in f:
                        line = line.strip()
                        if line == '':
                            continue  # Skip sentence boundaries
                        parts = line.split('\t')
                        if len(parts) == 2:
                            word, true_tag = parts
                            true_tag = true_tag.strip()  # Strip whitespace from tag
                            predicted = self.predict(word)
                            total += 1
                            if predicted == true_tag:
                                correct += 1
                    break  # Success, exit encoding loop
            except (UnicodeDecodeError, Exception) as e:
                continue  # Try next encoding
        
        if total == 0:
            return 0.0
        accuracy = (correct / total) * 100
        return round(accuracy, 2)
if __name__ == "__main__":
    tagger = Tagger()
    tagger.train(sys.argv[1])
    tagger.save('tagger.model')
    
