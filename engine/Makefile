.RECIPEPREFIX = >
.PHONY: gen test build run

gen:
> go run github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen@v2.4.1 -config api/oapi-codegen.yaml api/engine.yaml

test:
> go test ./...

build:
> go build -o bin/engine ./cmd/engine

run:
> ENGINE_KEY=dev-key go run ./cmd/engine
