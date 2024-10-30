.PHONY: help plan setup clean
help: ## Show this help message
	@grep -E '^[a-zA-Z_./-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

plan: out.json ## Plan the AKs

setup: .venv/deps ## setup runtime

.venv:
	python3 -m venv ".venv" && (echo "PATH_add ./.venv/bin" > ".envrc")
	command -v direnv >/dev/null && direnv allow

.venv/deps: .venv ak-plan-optimierung deps/requirements.txt
	.venv/bin/pip install -r deps/requirements.txt
	pip install ./ak-plan-optimierung
	touch .venv/deps

clean: ## Clean up
	rm -rf .venv out.json input.json

out.json: input.json .venv/deps
	.venv/bin/python -m akplan.solve --threads "$$(nproc)" --gap_rel 9 input.json
	mv out-input.json out.json

input.json: config.yaml .venv/deps
	.venv/bin/python deps/generate_input_json.py config.yaml input.json
