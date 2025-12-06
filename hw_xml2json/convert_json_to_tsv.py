#!/usr/bin/env python3
"""
Converts JSON file back to TSV format
write a Python script that reads the JSON file and converts it back to the TSV format identitical with the tsv format used at the beginning; name it sample.tsv
"""

import json

def json2tsv(input_file, output_file):
    """
    Converts JSON back to TSV format:
    # sentence-text: <text>
    id\tform\tlemma\tpos\thead
    id\tform\tlemma\tpos\thead
    ...
    (empty line between sentences)
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence_data in data['corpus']:
            # Write the sentence text comment
            sentence_text = sentence_data.get('sentence', '')
            f.write(f'# sentence-text: {sentence_text}\n')
            
            # Write all tokens for this sentence
            tokens = sentence_data.get('tokens', [])
            for token in tokens:
                token_id = token.get('id', '')
                form = token.get('form', '')
                lemma = token.get('lemma', '')
                pos = token.get('pos', '')
                head = token.get('head', '')
                
                # Write tab-separated line
                f.write(f'{token_id}\t{form}\t{lemma}\t{pos}\t{head}\n')
            
            # Add empty line between sentences
            f.write('\n')

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python convert_json_to_tsv.py <input_file> <output_file>")
        sys.exit(1)

    json2tsv(sys.argv[1], sys.argv[2])