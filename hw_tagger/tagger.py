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
Uses word->tag mapping, context (previous tag), and suffix patterns for unknown words
"""

import sys
import pickle
from collections import defaultdict, Counter
import re

class Tagger:
    def __init__(self):
        self.model = {}  # Dictionary: word -> most common tag
        self.default_tag = 'N'  # Default tag for unknown words

        # Context models
        self.tag_bigrams = defaultdict(Counter)  # previous_tag -> current_tag
        self.word_tag_bigrams = defaultdict(lambda: defaultdict(Counter))  # previous_word -> current_word -> tag
        # Suffix patterns for unknown words
        self.suffix_patterns = defaultdict(Counter)  # suffix -> tag

        # Context tracking for sequential prediction
        self.previous_tag = None
        self.previous_word = None

    def _get_suffixes(self, word, max_len=4):
        """Extract suffixes of different lengths"""
        if len(word) < 2:
            return []
        suffixes = []
        for i in range(2, min(max_len + 1, len(word) + 1)):
            suffixes.append(word[-i:].lower())
        return suffixes

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

        previous_tag = None
        previous_word = None

        # Try UTF-8 first, then fall back to iso-8859-2
        encodings = ['utf-8', 'iso-8859-2', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    for line in f:
                        line = line.strip()
                        if line == '':
                            # Sentence boundary - reset context
                            previous_tag = None
                            previous_word = None
                            continue
                        
                        parts = line.split('\t')
                        if len(parts) == 2:
                            word = parts[0]
                            tag = parts[1].strip()
                            if tag:
                                word_tag_counts[word][tag] += 1
                                all_tags[tag] += 1
                                
                                # Learn tag bigrams
                                if previous_tag is not None:
                                    self.tag_bigrams[previous_tag][tag] += 1
                                
                                # Learn word-tag bigrams
                                if previous_word is not None:
                                    self.word_tag_bigrams[previous_word][word][tag] += 1
                                
                                # Learn suffix patterns (for unknown words)
                                suffixes = self._get_suffixes(word)
                                for suffix in suffixes:
                                    self.suffix_patterns[suffix][tag] += 1
                                
                                previous_tag = tag
                                previous_word = word
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
                pickle.dump({
                    'model': self.model, 
                    'default_tag': self.default_tag,
                    'tag_bigrams': dict(self.tag_bigrams),
                    'word_tag_bigrams': {k: dict(v) for k, v in self.word_tag_bigrams.items()},
                    'suffix_patterns': dict(self.suffix_patterns)
                }, f)
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
                    # Load context models
                    tag_bigrams_data = data.get('tag_bigrams', {})
                    self.tag_bigrams = defaultdict(Counter)
                    for prev_tag, next_tags in tag_bigrams_data.items():
                        self.tag_bigrams[prev_tag] = Counter(next_tags)
                    
                    word_tag_bigrams_data = data.get('word_tag_bigrams', {})
                    self.word_tag_bigrams = defaultdict(lambda: defaultdict(Counter))
                    for prev_word, word_tags in word_tag_bigrams_data.items():
                        for word, tags in word_tags.items():
                            self.word_tag_bigrams[prev_word][word] = Counter(tags)
                    
                    suffix_patterns_data = data.get('suffix_patterns', {})
                    self.suffix_patterns = defaultdict(Counter)
                    for suffix, tags in suffix_patterns_data.items():
                        self.suffix_patterns[suffix] = Counter(tags)
        except Exception as e:
            self.model = {}
            self.default_tag = 'N'
            self.tag_bigrams = defaultdict(Counter)
            self.word_tag_bigrams = defaultdict(lambda: defaultdict(Counter))
            self.suffix_patterns = defaultdict(Counter)

        # Reset context
        self.previous_tag = None
        self.previous_word = None
                
    def predict(self, word):
        """
        predicts and returns the POS tag for a given word
        must be a valid 1-letter POS tag for any word
        """
        # If word is known, trust the stored tag (no context override)
        if word in self.model:
            return self.model[word]
        
        # For unknown words, use multiple features with scoring
        scores = Counter()
        
        # Feature 1: Context - previous tag bigram (strong signal)
        if self.previous_tag is not None and self.previous_tag in self.tag_bigrams:
            for tag, count in self.tag_bigrams[self.previous_tag].items():
                scores[tag] += count * 3  # Weight context
        
        # Feature 2: Context - previous word -> current word bigram (very strong signal)
        if self.previous_word is not None and self.previous_word in self.word_tag_bigrams:
            if word in self.word_tag_bigrams[self.previous_word]:
                for tag, count in self.word_tag_bigrams[self.previous_word][word].items():
                    scores[tag] += count * 5  # Higher weight for word context
        
        # Feature 3: Suffix patterns (morphological clues)
        suffixes = self._get_suffixes(word)
        for suffix in suffixes:
            if suffix in self.suffix_patterns:
                for tag, count in self.suffix_patterns[suffix].items():
                    scores[tag] += count
        
        # Feature 4: Word shape heuristics
        if word and len(word) > 0:
            if word[0].isupper() and len(word) > 1:
                # Capitalized words are often nouns (proper nouns)
                scores['N'] += 2
            if word.isdigit() or (word.replace(',', '').replace('.', '').isdigit()):
                scores['C'] += 10  # Numbers are almost always numerals
            if len(word) == 1 and word.isalpha():
                # Single letter words are often prepositions or conjunctions
                scores['R'] += 2
                scores['J'] += 2
            # Punctuation detection
            if word in [',', '.', ':', ';', '!', '?', '-', '(', ')', '[', ']', '{', '}']:
                scores['Z'] += 10
        
        # Return best scoring tag, or default
        if scores:
            return scores.most_common(1)[0][0]
        return self.default_tag
        
        
    def predict_all(self, filename):
        """
        predicts POS tags for all words in a file
        the format of the file is one word per line, or an empty line for sentence boundary, UTF-8 encoding
        the output should be returned as a list of the POS labels, or an empty string for sentence boundary e.g. ['N', 'V', 'Z', '', 'R']
        """
        results = []
        # Reset context at start
        self.previous_tag = None
        self.previous_word = None
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line == '':
                        results.append('')
                        # Reset context on sentence boundary
                        self.previous_tag = None
                        self.previous_word = None
                    else:
                        predicted = self.predict(line)
                        results.append(predicted)
                        # Update context for next prediction
                        self.previous_tag = predicted
                        self.previous_word = line
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
        # Reset context at start
        self.previous_tag = None
        self.previous_word = None
        
        # Try multiple encodings like in train()
        encodings = ['utf-8', 'iso-8859-2', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    for line in f:
                        line = line.strip()
                        if line == '':
                            # Reset context on sentence boundary
                            self.previous_tag = None
                            self.previous_word = None
                            continue  # Skip sentence boundaries
                        parts = line.split('\t')
                        if len(parts) == 2:
                            word, true_tag = parts
                            true_tag = true_tag.strip()  # Strip whitespace from tag
                            predicted = self.predict(word)
                            total += 1
                            if predicted == true_tag:
                                correct += 1
                            # Update context for next prediction
                            self.previous_tag = predicted
                            self.previous_word = word
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
    
