#!/usr/bin/env python3
"""
Converts XML file to json format
write a Python script that reads the XML file and converts it into a JSON file; name it sample.json
"""
import json
from pydoc import text
import xml.etree.ElementTree  as ET

def xml2json(input_file, output_file):
    """
    structure:
    {
    "corpus": [
        {
            "sentence": "...",
            "tokens": [
                {
                    "id": "1",
                    "form": "...",
                    "lemma": "...",
                    "pos": "...",
                    "head": "..."
                },
                ...
            ]
        },
        ...
    ]
    }
    """    
    # parsing the XML file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # build the JSON struct
    corpus = []

    # iterate through all sentence elements
    for sentence_elem in root.findall('sentence'):
        sentence_data = {}

        # get the text element
        text_elem = sentence_elem.find('text')
        if text_elem is not None and text_elem.text:
            sentence_data['sentence'] = text_elem.text.strip()
        
        # get all token elements
        tokens = []
        for token_elem in sentence_elem.findall('token'):
            token_data = {}
            
            # Extract all token fields
            id_elem = token_elem.find('id')
            if id_elem is not None and id_elem.text:
                token_data['id'] = int(id_elem.text.strip())
            
            form_elem = token_elem.find('form')
            if form_elem is not None and form_elem.text:
                token_data['form'] = form_elem.text.strip()
            
            lemma_elem = token_elem.find('lemma')
            if lemma_elem is not None and lemma_elem.text:
                token_data['lemma'] = lemma_elem.text.strip()
            
            pos_elem = token_elem.find('pos')
            if pos_elem is not None and pos_elem.text:
                token_data['pos'] = pos_elem.text.strip()
            
            head_elem = token_elem.find('head')
            if head_elem is not None and head_elem.text:
                token_data['head'] = int(head_elem.text.strip())
            
            tokens.append(token_data)
        
        sentence_data['tokens'] = tokens
        corpus.append(sentence_data)
    
    # Create the final JSON structure
    json_data = {
        'corpus': corpus
    }
    
    # Write to JSON file with pretty formatting
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python convert_xml_to_json.py <input_file> <output_file>")
        sys.exit(1)

    xml2json(sys.argv[1], sys.argv[2])
