VENDOR_DIR = vendor

.PHONY: pull run clean

pull:
	@mkdir -p $(VENDOR_DIR)
	@if [ -d "$(VENDOR_DIR)/A-maze-ing" ]; then \
		echo "Updating A-maze-ing..."; \
		git -C $(VENDOR_DIR)/A-maze-ing pull --quiet; \
	else \
		echo "Cloning A-maze-ing..."; \
		git clone https://github.com/maya-fakih/A-maze-ing.git $(VENDOR_DIR)/A-maze-ing; \
	fi
	@if [ -d "$(VENDOR_DIR)/ML_model_evaluation" ]; then \
		echo "Updating ML_model_evaluation..."; \
		git -C $(VENDOR_DIR)/ML_model_evaluation pull --quiet; \
	else \
		echo "Cloning ML_model_evaluation..."; \
		git clone https://github.com/maya-fakih/ML_model_evaluation.git $(VENDOR_DIR)/ML_model_evaluation; \
	fi
	@echo "Done! Repos available in $(VENDOR_DIR)/"

run:
	python run_gui.py

clean:
	rm -rf $(VENDOR_DIR)/
