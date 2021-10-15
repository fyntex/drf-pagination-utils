VCS_REVISION_ID = $(vcs_last_revision_id)$(vcs_dirty_tag)
VCS_REVISION_SHORT_ID = $(vcs_last_revision_short_id)$(vcs_dirty_tag)
VCS_DIRTY = $(shell test -z "$$(test -d .git && git status --porcelain)" && echo 'false' || echo 'true')
VCS_REV_TIMESTAMP = $(shell date --date="@$(VCS_REV_TIMESTAMP_UNIX)" +'%Y-%m-%dT%H:%M:%S%z')
VCS_REV_TIMESTAMP_UNIX = $(shell git log -1 --pretty=format:%ct HEAD)
VCS_URL = $(shell git config --get remote.origin.url)
vcs_last_revision_id = $(shell git rev-parse HEAD)
vcs_last_revision_short_id = $(shell git rev-parse --short=8 HEAD)
vcs_dirty_tag = $(shell test "$(VCS_DIRTY)" = true && echo '.dirty')

.PHONY: vcs-check-dirty
vcs-check-dirty: ## Check if working tree of VCS repository is clean
	@test "$(VCS_DIRTY)" = "true" && echo "*** VCS is dirty." && exit 1 || true
