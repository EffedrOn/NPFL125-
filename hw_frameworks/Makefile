SHELL=/bin/bash

# Variables
MODEL_DIR = models
DATA_DIR = data
CONFIG_FILE = config.cfg
BASE_CONFIG = base_config.cfg
TRAIN_DATA = $(DATA_DIR)/train.spacy
DEV_DATA = $(DATA_DIR)/dev.spacy
TEST_DATA = $(DATA_DIR)/test.spacy
MODEL_BEST = $(MODEL_DIR)/model-best

# UD Slovak treebank repository
UD_REPO = https://github.com/UniversalDependencies/UD_Slovak-SNK.git
UD_DIR = UD_Slovak-SNK
UD_BRANCH = master

# CoNLL-U file paths (after cloning)
TRAIN_CONLLU = $(UD_DIR)/sk_snk-ud-train.conllu
DEV_CONLLU = $(UD_DIR)/sk_snk-ud-dev.conllu
TEST_CONLLU = $(UD_DIR)/sk_snk-ud-test.conllu

.PHONY: readme download train eval show clean

readme:
	@echo "TODO: Add your readme text here"
	@echo "I used spaCy framework, ..."
	@echo "I trained ... model on ... data for ... language"
	@echo "The accuracy is ...%, which seems ... to me"
	@echo "I noticed ... behavior, it does ... well, it makes ... errors"

download: $(TRAIN_DATA) $(DEV_DATA) $(TEST_DATA)
	@echo "Data download complete!"
	@echo "Training data: $(TRAIN_DATA)"
	@echo "Dev data: $(DEV_DATA)"
	@echo "Test data: $(TEST_DATA)"

# Download and convert training data
$(TRAIN_DATA): $(TRAIN_CONLLU)
	@echo "Converting training data to spaCy format..."
	@mkdir -p $(DATA_DIR)
	@python3 -m spacy convert $(TRAIN_CONLLU) $(DATA_DIR) 
	@# Rename to expected filename
	@if [ -f "$(DATA_DIR)/sk_snk-ud-train.spacy" ]; then \
		mv $(DATA_DIR)/sk_snk-ud-train.spacy $(TRAIN_DATA); \
	fi
	@echo "Training data ready: $(TRAIN_DATA)"

# Download and convert dev data
$(DEV_DATA): $(DEV_CONLLU)
	@echo "Converting dev data to spaCy format..."
	@mkdir -p $(DATA_DIR)
	@python3 -m spacy convert $(DEV_CONLLU) $(DATA_DIR) 
	@# Rename to expected filename
	@if [ -f "$(DATA_DIR)/sk_snk-ud-dev.spacy" ]; then \
		mv $(DATA_DIR)/sk_snk-ud-dev.spacy $(DEV_DATA); \
	fi
	@echo "Dev data ready: $(DEV_DATA)"

# Download and convert test data
$(TEST_DATA): $(TEST_CONLLU)
	@echo "Converting test data to spaCy format..."
	@mkdir -p $(DATA_DIR)
	@python3 -m spacy convert $(TEST_CONLLU) $(DATA_DIR)
	@# Rename to expected filename
	@if [ -f "$(DATA_DIR)/sk_snk-ud-test.spacy" ]; then \
		mv $(DATA_DIR)/sk_snk-ud-test.spacy $(TEST_DATA); \
	fi
	@echo "Test data ready: $(TEST_DATA)"

# Clone UD repository if it doesn't exist
$(TRAIN_CONLLU) $(DEV_CONLLU) $(TEST_CONLLU):
	@echo "Downloading Slovak UD treebank from GitHub..."
	@if [ ! -d "$(UD_DIR)" ]; then \
		echo "Cloning $(UD_REPO)..."; \
		git clone --depth 1 --branch $(UD_BRANCH) $(UD_REPO) $(UD_DIR); \
	else \
		echo "Repository $(UD_DIR) already exists, skipping clone."; \
	fi
	@# Verify files exist
	@if [ ! -f "$(TRAIN_CONLLU)" ]; then \
		echo "Error: $(TRAIN_CONLLU) not found. Checking repository structure..."; \
		ls -la $(UD_DIR)/*.conllu 2>/dev/null || echo "No .conllu files found in $(UD_DIR)"; \
		exit 1; \
	fi
	@if [ ! -f "$(DEV_CONLLU)" ]; then \
		echo "Warning: $(DEV_CONLLU) not found."; \
	fi
	@if [ ! -f "$(TEST_CONLLU)" ]; then \
		echo "Warning: $(TEST_CONLLU) not found."; \
	fi
	@echo "CoNLL-U files downloaded successfully!"

train: $(CONFIG_FILE) $(TRAIN_DATA) $(DEV_DATA)
	@echo "Training spaCy model..."
	@mkdir -p $(MODEL_DIR)
	@# Check if model already exists
	@if [ -d "$(MODEL_BEST)" ]; then \
		echo "Model already trained at $(MODEL_BEST). Skipping training."; \
		echo "To retrain, run 'make clean' first."; \
	else \
		python3 -m spacy train $(CONFIG_FILE) \
			--output ./$(MODEL_DIR) \
			--paths.train $(TRAIN_DATA) \
			--paths.dev $(DEV_DATA); \
	fi

eval: $(MODEL_BEST) $(TEST_DATA)
	@echo "Evaluating model..."
	@# Must NOT retrain if already trained - just evaluate
	@if [ ! -d "$(MODEL_BEST)" ]; then \
		echo "Error: Model not found. Run 'make train' first."; \
		exit 1; \
	fi
	@if [ ! -f "$(TEST_DATA)" ]; then \
		echo "Error: Test data not found. Run 'make download' first."; \
		exit 1; \
	fi
	@python3 -m spacy evaluate $(MODEL_BEST) $(TEST_DATA)

show: $(MODEL_BEST)
	@echo "Applying model to sample sentences..."
	@# Must NOT retrain if already trained - just show results
	@if [ ! -d "$(MODEL_BEST)" ]; then \
		echo "Error: Model not found. Run 'make train' first."; \
		exit 1; \
	fi
	@echo "TODO: Add Python script or inline Python to show model results"
	@# Example:
	@# python3 -c "import spacy; nlp = spacy.load('$(MODEL_BEST)'); \
	@#   doc = nlp('Sample sentence here'); \
	@#   for token in doc: print(f'{token.text}\t{token.pos_}\t{token.tag_}')"

# Helper target to ensure config file exists
$(CONFIG_FILE): $(BASE_CONFIG)
	@if [ ! -f "$(BASE_CONFIG)" ]; then \
		echo "Error: $(BASE_CONFIG) not found. Download it from https://spacy.io/usage/training#quickstart"; \
		exit 1; \
	fi
	@echo "Filling config file from base config..."
	@python3 -m spacy init fill-config $(BASE_CONFIG) $(CONFIG_FILE)

clean:
	@echo "Cleaning generated files..."
	@rm -rf $(MODEL_DIR)
	@rm -rf $(DATA_DIR)
	@rm -f $(CONFIG_FILE)
	@echo "Note: $(UD_DIR) directory is preserved. To remove it, run: rm -rf $(UD_DIR)"