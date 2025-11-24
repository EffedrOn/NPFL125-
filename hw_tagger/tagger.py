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
HMM-based POS tagger with Viterbi decoding
Uses transition probabilities (tag->tag) and emission probabilities (tag->word)
"""

import sys
import pickle
from collections import defaultdict, Counter
import math

class Tagger:
    def __init__(self):
        self.model = {}  # Dictionary: word -> most common tag 
        self.default_tag = 'N'  # Default tag for unknown words

        # HMM components
        self.transition_counts = defaultdict(Counter)  # previous_tag -> current_tag counts
        self.emission_counts = defaultdict(lambda: defaultdict(int))  # tag -> word counts
        self.tag_counts = Counter()  # Overall tag frequencies
        self.start_tag_counts = Counter()  # Tags at sentence start
        
        # For unknown word handling
        self.suffix_patterns = defaultdict(Counter)  # suffix -> tag
        self.all_tags = set()  # Set of all possible tags
        
        


    def _get_suffixes(self, word, max_len=6):
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
        Trains HMM transition and emission probabilities
        """

        # Count all word->tag pairs (for backward compatibility)
        word_tag_counts = defaultdict(Counter)
        all_tags = Counter()

        previous_tag = None
        sentence_start = True

        encodings = ['utf-8', 'iso-8859-2', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    for line in f:
                        line = line.strip()
                        if line == '':
                            # Sentence boundary - reset context
                            previous_tag = None
                            sentence_start = True
                            continue
                        
                        parts = line.split('\t')
                        if len(parts) == 2:
                            word = parts[0]
                            tag = parts[1].strip()
                            if tag:
                                # Count word->tag pairs
                                word_tag_counts[word][tag] += 1
                                all_tags[tag] += 1
                                self.all_tags.add(tag)
                                
                                # Count emissions: tag -> word
                                self.emission_counts[tag][word] += 1
                                self.tag_counts[tag] += 1
                                
                                # Count transitions: previous_tag -> current_tag
                                if previous_tag is not None:
                                    self.transition_counts[previous_tag][tag] += 1
                                
                                # Track sentence start tags
                                if sentence_start:
                                    self.start_tag_counts[tag] += 1
                                
                                # Learn suffix patterns (for unknown words)
                                suffixes = self._get_suffixes(word)
                                for suffix in suffixes:
                                    self.suffix_patterns[suffix][tag] += 1
                                
                                previous_tag = tag
                                sentence_start = False
                    break  # Success
            except (UnicodeDecodeError, Exception) as e:
                continue  
        
        # Store most common tag for each word (for backward compatibility)
        for word, tag_counts in word_tag_counts.items():
            self.model[word] = tag_counts.most_common(1)[0][0]
        
        # Set default tag to most common tag overall
        if all_tags:
            self.default_tag = all_tags.most_common(1)[0][0]

    def _log_probability(self, count, total, smoothing=1.0):
        """Calculate log probability with add-one smoothing"""
        if total == 0:
            return -float('inf')
        return math.log((count + smoothing) / (total + smoothing * len(self.all_tags)))

    def _get_emission_log_prob(self, tag, word):
        """Get log probability of word given tag, with smoothing for unknown words"""
        # Known word
        if word in self.emission_counts[tag]:
            count = self.emission_counts[tag][word]
            total = self.tag_counts[tag]
            return self._log_probability(count, total)
        
        # Unknown word - use suffix patterns and heuristics
        log_prob = -10.0  # Base penalty for unknown words
        
        # Use suffix patterns
        suffixes = self._get_suffixes(word)
        suffix_score = 0.0
        for suffix in suffixes:
            if suffix in self.suffix_patterns:
                if tag in self.suffix_patterns[suffix]:
                    suffix_score += math.log(1 + self.suffix_patterns[suffix][tag])
        
        if suffix_score > 0:
            log_prob = -5.0 + suffix_score * 0.1
        
        # Word shape heuristics
        if word and len(word) > 0:
            if word[0].isupper() and len(word) > 1:
                if tag == 'N':  # Proper nouns
                    log_prob += 1.0
            if word.isdigit() or (word.replace(',', '').replace('.', '').isdigit()):
                if tag == 'C':  # Numerals
                    log_prob += 3.0
            if len(word) == 1 and word.isalpha():
                if tag in ['R', 'J']:  # Prepositions/conjunctions
                    log_prob += 1.0
            if word in [',', '.', ':', ';', '!', '?', '-', '(', ')', '[', ']', '{', '}']: # maybe here woul be better to just check if it is not letter or numnber
                if tag == 'Z':  # Punctuation
                    log_prob += 3.0
        
        # Fallback: use tag frequency
        if self.tag_counts[tag] > 0:
            tag_freq = self.tag_counts[tag] / sum(self.tag_counts.values())
            log_prob += math.log(tag_freq) * 0.5
        
        return log_prob

    def _get_transition_log_prob(self, prev_tag, curr_tag):
        """Get log probability of transition from prev_tag to curr_tag"""
        if prev_tag in self.transition_counts:
            count = self.transition_counts[prev_tag][curr_tag]
            total = sum(self.transition_counts[prev_tag].values())
            return self._log_probability(count, total)
        # Unknown transition - use tag frequency
        if self.tag_counts[curr_tag] > 0:
            tag_freq = self.tag_counts[curr_tag] / sum(self.tag_counts.values())
            return math.log(tag_freq) - 2.0  # Penalty for unknown transition
        return -10.0

    def _get_start_log_prob(self, tag):
        """Get log probability of tag at sentence start"""
        if self.start_tag_counts[tag] > 0:
            total_starts = sum(self.start_tag_counts.values())
            return self._log_probability(self.start_tag_counts[tag], total_starts)
        # Fallback to tag frequency
        if self.tag_counts[tag] > 0:
            tag_freq = self.tag_counts[tag] / sum(self.tag_counts.values())
            return math.log(tag_freq) - 1.0
        return -10.0

    def _viterbi(self, words):
        """Viterbi algorithm to find most likely tag sequence"""
        
        n = len(words)
        if n == 0:
            return []
        
        # Get all possible tags
        tags = list(self.all_tags) if self.all_tags else [self.default_tag]
        if not tags:
            return [self.default_tag] * n
        
        # Initialize DP table: viterbi[i][tag] = best log probability ending at position i with tag
        viterbi = [{} for _ in range(n)]
        backpointer = [{} for _ in range(n)]
        
        # Initialize first position
        for tag in tags:
            start_prob = self._get_start_log_prob(tag)
            emission_prob = self._get_emission_log_prob(tag, words[0])
            viterbi[0][tag] = start_prob + emission_prob
            backpointer[0][tag] = None
        
        # Filling DP table
        for i in range(1, n):
            for curr_tag in tags:
                best_prob = -float('inf')
                best_prev_tag = None
                
                emission_prob = self._get_emission_log_prob(curr_tag, words[i])
                
                for prev_tag in tags:
                    transition_prob = self._get_transition_log_prob(prev_tag, curr_tag)
                    prob = viterbi[i-1][prev_tag] + transition_prob + emission_prob
                    
                    if prob > best_prob:
                        best_prob = prob
                        best_prev_tag = prev_tag
                
                viterbi[i][curr_tag] = best_prob
                backpointer[i][curr_tag] = best_prev_tag
        
        # Backtrack to find best path
        # Find best final tag
        best_final_prob = -float('inf')
        best_final_tag = None
        for tag in tags:
            if viterbi[n-1][tag] > best_final_prob:
                best_final_prob = viterbi[n-1][tag]
                best_final_tag = tag
        
        # Backtrack
        path = []
        curr_tag = best_final_tag
        for i in range(n-1, -1, -1):
            path.append(curr_tag)
            curr_tag = backpointer[i][curr_tag]
        
        path.reverse()
        return path
            
    def save(self, filename):
        """
        saves the tagging model to a file using pickle
        """
        try:
            with open(filename, 'wb') as f:
                pickle.dump({
                    'model': self.model, 
                    'default_tag': self.default_tag,
                    'transition_counts': {k: dict(v) for k, v in self.transition_counts.items()},
                    'emission_counts': {k: dict(v) for k, v in self.emission_counts.items()},
                    'tag_counts': dict(self.tag_counts),
                    'start_tag_counts': dict(self.start_tag_counts),
                    'suffix_patterns': dict(self.suffix_patterns),
                    'all_tags': list(self.all_tags)
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
                
                # Load HMM components
                transition_data = data.get('transition_counts', {})
                self.transition_counts = defaultdict(Counter)
                for prev_tag, next_tags in transition_data.items():
                    self.transition_counts[prev_tag] = Counter(next_tags)
                
                emission_data = data.get('emission_counts', {})
                self.emission_counts = defaultdict(lambda: defaultdict(int))
                for tag, words in emission_data.items():
                    self.emission_counts[tag] = defaultdict(int, words)
                
                self.tag_counts = Counter(data.get('tag_counts', {}))
                self.start_tag_counts = Counter(data.get('start_tag_counts', {}))
                
                suffix_patterns_data = data.get('suffix_patterns', {})
                self.suffix_patterns = defaultdict(Counter)
                for suffix, tags in suffix_patterns_data.items():
                    self.suffix_patterns[suffix] = Counter(tags)
                
                self.all_tags = set(data.get('all_tags', []))
        except Exception as e:
            self.model = {}
            self.default_tag = 'N'
            self.transition_counts = defaultdict(Counter)
            self.emission_counts = defaultdict(lambda: defaultdict(int))
            self.tag_counts = Counter()
            self.start_tag_counts = Counter()
            self.suffix_patterns = defaultdict(Counter)
            self.all_tags = set()

        
                
    def predict(self, word):
        """
        predicts and returns the POS tag for a given word
        must be a valid 1-letter POS tag for any word
        This method is kept for backward compatibility but uses simple lookup
        """
        # If word is known, trust the stored tag
        if word in self.model:
            return self.model[word]
        
        # For unknown words, use suffix patterns and heuristics
        scores = Counter()
        
        # Use suffix patterns
        suffixes = self._get_suffixes(word)
        for suffix in suffixes:
            if suffix in self.suffix_patterns:
                for tag, count in self.suffix_patterns[suffix].items():
                    scores[tag] += count
        
        # Word shape heuristics
        if word and len(word) > 0:
            if word[0].isupper() and len(word) > 1:
                scores['N'] += 2
            if word.isdigit() or (word.replace(',', '').replace('.', '').isdigit()):
                scores['C'] += 10
            if len(word) == 1 and word.isalpha():
                scores['R'] += 2
                scores['J'] += 2
            if word in [',', '.', ':', ';', '!', '?', '-', '(', ')', '[', ']', '{', '}']:
                scores['Z'] += 10
        
        # Return best scoring tag, or default
        if scores:
            return scores.most_common(1)[0][0]
        return self.default_tag
        
        
    def predict_all(self, filename):
        """
        predicts POS tags for all words in a file using Viterbi algorithm
        the format of the file is one word per line, or an empty line for sentence boundary, UTF-8 encoding
        the output should be returned as a list of the POS labels, or an empty string for sentence boundary e.g. ['N', 'V', 'Z', '', 'R']
        """
        results = []
        current_sentence = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line == '':
                        # Process accumulated sentence with Viterbi
                        if current_sentence:
                            tags = self._viterbi(current_sentence)
                            results.extend(tags)
                            current_sentence = []
                        results.append('')
                    else:
                        current_sentence.append(line)
                
                # Process last sentence if file doesn't end with empty line
                if current_sentence:
                    tags = self._viterbi(current_sentence)
                    results.extend(tags)
        except Exception as e:
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line == '':
                            results.append('')
                            
                        else:
                            predicted = self.predict(line)
                            results.append(predicted)
                            #self.previous_tag = predicted
                            #self.previous_word = line
            except:
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
        current_sentence_words = []
        current_sentence_true_tags = []
        
        # Try multiple encodings like in train()
        encodings = ['utf-8', 'iso-8859-2', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    for line in f:
                        line = line.strip()
                        if line == '':
                            # Process sentence with Viterbi
                            if current_sentence_words:
                                predicted_tags = self._viterbi(current_sentence_words)
                                for pred_tag, true_tag in zip(predicted_tags, current_sentence_true_tags):
                                    total += 1
                                    if pred_tag == true_tag:
                                        correct += 1
                                current_sentence_words = []
                                current_sentence_true_tags = []
                            continue
                        
                        parts = line.split('\t')
                        if len(parts) == 2:
                            word, true_tag = parts
                            true_tag = true_tag.strip()
                            current_sentence_words.append(word)
                            current_sentence_true_tags.append(true_tag)
                    
                    # Process last sentence if file doesn't end with empty line
                    if current_sentence_words:
                        predicted_tags = self._viterbi(current_sentence_words)
                        for pred_tag, true_tag in zip(predicted_tags, current_sentence_true_tags):
                            total += 1
                            if pred_tag == true_tag:
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
    
