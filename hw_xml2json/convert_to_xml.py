#!/usr/bin/env python3
"""
Converts TSV dependency tree format to XML
Each TSV column becomes a separate XML element
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom


def tsv2xml(input_file, output_file):
    """
    Structure:
    <corpus>
        <sentence>
            <text>...</text>
            <token>
                <id>1</id>
                <form>From</form>
                <lemma>from</lemma>
                <pos>ADP</pos>
                <head>3</head>
            </token>
            ...
        </sentence>
        ...
    </corpus>
    """
    root = ET.Element('corpus')

    current_sentence = None

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # skipping the empty lines
            if not line:
                continue
            
            # Check for sentence text comment
            if line.startswith('# sentence-text:'):
                if current_sentence is not None:
                    root.append(current_sentence)
                
                # Extract the sentence text
                sentence_text = line.replace('# sentence-text:', '').strip()

                current_sentence = ET.Element('sentence')

                # add text as a child element
                text_elem = ET.SubElement(current_sentence, 'text')
                text_elem.text = sentence_text
                continue
        
            # Parse token line
            parts = line.split("\t")
            if len(parts) == 5:
                current_token = ET.Element('token') 
                
                id_num = ET.SubElement(current_token, 'id')
                id_num.text = parts[0]

                form_elem = ET.SubElement(current_token, 'form')
                form_elem.text = parts[1]

                lemma_elem = ET.SubElement(current_token, 'lemma')
                lemma_elem.text = parts[2]
                
                pos_elem = ET.SubElement(current_token, 'pos')
                pos_elem.text = parts[3]
                
                head_elem = ET.SubElement(current_token, 'head')
                head_elem.text = parts[4]

                if current_sentence is not None:
                    current_sentence.append(current_token)
        
        # append the last sentence if it exists
        if current_sentence is not None:
            root.append(current_sentence)
        
        tree = ET.ElementTree(root)

        # Convert to string and pretty print
        xml_str = ET.tostring(root, encoding = 'unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="   ")

        # Remove extra blank lines
        pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
                
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python convert_to_xml.py <input_file> <output_file>")
        sys.exit(1)

    tsv2xml(sys.argv[1], sys.argv[2])