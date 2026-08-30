.DEFAULT_GOAL := help

.PHONY: help
help: ## Показать доступные команды
	@awk 'BEGIN {FS = ":.*##"; printf "Доступные команды:\n"} /^[a-zA-Z_-]+:.*?##/ {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
