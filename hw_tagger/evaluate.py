from tagger import Tagger

tagger = Tagger()
tagger.load('tagger.model')

# Debug: Check if model loaded correctly
print(f"Model size: {len(tagger.model)} words")
print(f"Default tag: {tagger.default_tag}")
if len(tagger.model) > 0:
    # Show first few entries
    sample_words = list(tagger.model.items())[:5]
    print(f"Sample entries: {sample_words}")
else:
    print("WARNING: Model is empty!")

# Try evaluation
accuracy = tagger.eval('tagger-eval.tsv')
print(f"Accuracy: {accuracy}%")