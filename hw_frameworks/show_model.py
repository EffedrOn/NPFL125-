#!/usr/bin/env python3
import spacy
import sys

def show_model(model_path):
    nlp = spacy.load(model_path)
    sentences = [
        'Kde tá ľudská duša drieme?',
        'Prečo to tu píšem?',
        'Ďalšie kroky švajčiarskej sudkyne povedú do Belehradu.',
        'Slovensko je krásna krajina.',
        'Učím sa programovať v Pythone.'
    ]
    
    for i, sent in enumerate(sentences, 1):
        doc = nlp(sent)
        sep = '=' * 70
        print(f'\n{sep}')
        print(f'Sentence {i}: {sent}')
        print(sep)
        print(f'{"Token":<20} {"POS":<10} {"Tag":<15} {"Dep":<15} {"Head":<15}')
        print('-' * 70)
        for token in doc:
            print(f'{token.text:<20} {token.pos_:<10} {token.tag_:<15} {token.dep_:<15} {token.head.text:<15}')

if __name__ == '__main__':
    model_path = sys.argv[1] if len(sys.argv) > 1 else 'models/model-best'
    show_model(model_path)