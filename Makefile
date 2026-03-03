SRC_DIR = src
BUILD_DIR = build
PAGES_DIR = $(SRC_DIR)/pages
HTML_SOURCES := $(wildcard $(PAGES_DIR)/*.html)
BUILD_TARGETS := $(patsubst $(PAGES_DIR)/%.html,$(BUILD_DIR)/%.html,$(HTML_SOURCES))

$(BUILD_DIR): CNAME $(HTML_SOURCES)
	mkdir -p ./build
	cp CNAME $@

$(BUILD_DIR)/%.html: $(PAGES_DIR)/%.html | $(BUILD_DIR)
	bin/render $< > $@

.PHONY: all
all: $(BUILD_TARGETS)

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
