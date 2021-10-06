.PHONY: help-tasks
help-tasks:
	@echo "Make tasks:"
	@awk \
	'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9._-]+:.*?## / {printf "%s\t%s\n", $$1, $$2}' \
		$(MAKEFILE_LIST) | sort | column -t -s $$'\t'

.PHONY: help-tasks-color
help-tasks-color:
	@echo "Make tasks:"
	@awk \
	'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9._-]+:.*?## / {printf "\033[36m%s\033[0m\t%s\n", $$1, $$2}' \
		$(MAKEFILE_LIST) | sort | column -t -s $$'\t'
