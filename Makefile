TOP_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
BIN_DIR = $(TOP_DIR)/bin
CONFIG_DIR = $(TOP_DIR)/config
SRC_DIR = $(TOP_DIR)/src
VAR_DIR = $(TOP_DIR)/var

ALL_TARGETS += build
BUILD_TARGETS += initialize
CHECK_TARGETS +=
CLEAN_TARGETS +=
DISTCLEAN_TARGETS += clean
FIX_TARGETS +=
INITIALIZE_TARGETS += install
INSTALL_TARGETS +=
TEST_TARGETS +=
UPDATE_TARGETS +=

-include $(CONFIG_DIR)/config.mk

include $(CONFIG_DIR)/Makefile.d/*/var.mk
-include $(CONFIG_DIR)/var.mk


.PHONY: all
all: $(ALL_TARGETS)

.PHONY: build
build: $(BUILD_TARGETS)

.PHONY: check
check: $(CHECK_TARGETS)

.PHONY: clean
clean: $(CLEAN_TARGETS)

.PHONY: distclean
distclean: $(DISTCLEAN_TARGETS)
	rm -rf $(VAR_DIR)/*

.PHONY: fix
fix: $(FIX_TARGETS)

.PHONY: initialize
initialize: $(INITIALIZE_TARGETS)

.PHONY: install
install: $(INSTALL_TARGETS)

.PHONY: test
test: $(TEST_TARGETS)

.PHONY: update
update: $(UPDATE_TARGETS)


include $(CONFIG_DIR)/Makefile.d/*/task.mk
-include $(CONFIG_DIR)/task.mk
