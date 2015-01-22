PREFIX ?= /usr/local
BINPREFIX ?= "$(PREFIX)/bin"
MANPREFIX ?= "$(PREFIX)/share/man/man1"

GIT_COMMANDS = git-changes git-fixup git-settings git-snapshot git-state git-upstream
GIT_COMMANDS_UTILITIES = git-commands-utils

install:
	@cp bin/git-* $(BINPREFIX)
	@cp man/man1/git-*.1 $(MANPREFIX)

uninstall:
	@$(foreach COMMAND_UTIL, $(GIT_COMMANDS_UTILITIES), \
		rm -f $(BINPREFIX)/$(COMMAND_UTIL); \
	)
	@$(foreach COMMAND, $(GIT_COMMANDS), \
		rm -f $(BINPREFIX)/$(COMMAND); \
		rm -f $(MANPREFIX)/$(COMMAND).1; \
	)
