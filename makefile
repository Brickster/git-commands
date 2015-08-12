PREFIX ?= /usr/local
BINPREFIX ?= "$(PREFIX)/bin"
MANPREFIX ?= "$(PREFIX)/share/man/man1"

GIT_COMMANDS = git-abandon git-changes git-fixup git-restash git-settings git-snapshot git-state git-upstream

install:
	@cp bin/git-* $(BINPREFIX)
	@mkdir -p $(BINPREFIX)/commands
	@cp bin/commands/* $(BINPREFIX)/commands
	@mkdir -p $(BINPREFIX)/utils
	@cp bin/utils/* $(BINPREFIX)/utils
	@mkdir -p $(MANPREFIX)
	@cp man/man1/git-*.1 $(MANPREFIX)

uninstall:
	@$(foreach COMMAND, $(GIT_COMMANDS), \
		rm -f $(BINPREFIX)/$(COMMAND); \
		rm -f $(MANPREFIX)/$(COMMAND).1; \
	)
	@rm -fdr $(BINPREFIX)/commands
	@rm -fdr $(BINPREFIX)/utils
