.PHONY: help plan setup clean importance
help: ## Show this help message
	@grep -E '^[a-zA-Z_./-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

plan: plan.md table.md personal_plan.md ## Plan the AKs

setup: .venv/deps ## setup runtime

.venv:
	python3 -m venv ".venv" && (echo "PATH_add ./.venv/bin" > ".envrc")
	command -v direnv >/dev/null && direnv allow

.venv/deps: .venv ak-plan-optimierung deps/requirements.txt
	.venv/bin/python -m pip install -r deps/requirements.txt
	.venv/bin/python -m pip install ./ak-plan-optimierung
	touch .venv/deps

clean: ## Clean up
	rm -rf .venv data

importance: data/input.json ## Calculate importance of AKs
	@.venv/bin/python deps/generate_ak_importance.py data/input.json

data/out.json: data/input.json .venv/deps
	cd data && ../.venv/bin/python -m akplan.solve --threads "$$(nproc)" --gap_rel 9 ./input.json
	mv data/out-input.json data/out.json

plan.md: data/out.json .venv/deps deps/generate_output_md.py
	.venv/bin/python deps/generate_output_md.py data/out.json plan.md

table.md: data/out.json .venv/deps deps/generate_output_md_table.py
	.venv/bin/python deps/generate_output_md_table.py data/out.json table.md

personal_plan.md: data/out.json .venv/deps deps/generate_output_md_table.py
	.venv/bin/python deps/generate_output_personal_md_table.py data/out.json personal_plan.md

data/input.json: data/config.yaml .venv/deps deps/generate_input_json.py
	.venv/bin/python deps/generate_input_json.py --penalize 0.4 data/config.yaml data/input.json

data/config.yaml: Planungssheet.ods config.yaml .venv/deps deps/generate_yaml_config_from_ods_sheet.py
	.venv/bin/python deps/generate_yaml_config_from_ods_sheet.py Planungssheet.ods config.yaml data/config.yaml
