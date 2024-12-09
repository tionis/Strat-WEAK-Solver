.PHONY: help plan setup clean
help: ## Show this help message
	@grep -E '^[a-zA-Z_./-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

plan: out.md table.md ## Plan the AKs

setup: .venv/deps ## setup runtime

.venv:
	python3 -m venv ".venv" && (echo "PATH_add ./.venv/bin" > ".envrc")
	command -v direnv >/dev/null && direnv allow

.venv/deps: .venv ak-plan-optimierung deps/requirements.txt
	.venv/bin/pip install -r deps/requirements.txt
	.venv/bin/pip install ./ak-plan-optimierung
	touch .venv/deps

clean: ## Clean up
	rm -rf .venv data

data/out.json: data/input.json .venv/deps
	cd data && ../.venv/bin/python -m akplan.solve --threads "$$(nproc)" --gap_rel 9 ./input.json
	mv data/out-input.json data/out.json

out.md: data/out.json .venv/deps deps/generate_output_md.py
	.venv/bin/python deps/generate_output_md.py data/out.json out.md

table.md: data/out.json .venv/deps deps/generate_output_md_table.py
	.venv/bin/python deps/generate_output_md_table.py data/out.json table.md

data/input.json: data/config.yaml .venv/deps deps/generate_input_json.py
	.venv/bin/python deps/generate_input_json.py data/config.yaml data/input.json

data/config.yaml: Planungssheet.ods config.yaml .venv/deps deps/generate_yaml_config_from_ods_sheet.py
	.venv/bin/python deps/generate_yaml_config_from_ods_sheet.py Planungssheet.ods config.yaml data/config.yaml
