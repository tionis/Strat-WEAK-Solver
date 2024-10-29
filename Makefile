.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_./-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

plan: out.json ## Plan the AKs

out.json: input.json .solver.docker.id
	docker run --rm -v "$$(PWD)/input.json:/input.json" -v "$(PWD)/out.json:/out-input.json" "$$(cat .docker.id)" -- python -m ak-plan-optimierung/akplan.solve --threads "$$(nproc)" --gap_rel 9 input.json

.solver.docker.id: deps/solver.Dockerfile
	docker build -t ak-solver --iidfile .docker.id deps/solver.Dockerfile

.parser.docker.id: deps/parser.Dockerfile
	docker build -t ak-parser --iidfile .parser.docker.id deps/parser.Dockerfile

input.json: aks.csv people.csv .parser.docker.id
	docker run --rm -v "$$(PWD)/aks.csv:/aks.csv" -v "$$(PWD)/people.csv:/people.csv" -v "$$(PWD)/input.json:/input.json" "$$(cat .parser.docker.id)" python3 /parse.py
