SRC_DIR = src
BUILD_DIR = build
PAGES_DIR = $(SRC_DIR)/pages
STATIC_DIR = $(SRC_DIR)/static
HTML_SOURCES := $(wildcard $(PAGES_DIR)/*.html)
STATIC_SOURCES := $(wildcard $(STATIC_DIR)/**/*.*)
BUILD_TARGETS := $(patsubst $(PAGES_DIR)/%.html,$(BUILD_DIR)/%.html,$(HTML_SOURCES))

$(BUILD_DIR): CNAME $(HTML_SOURCES)
	mkdir -p $(BUILD_DIR)
	cp CNAME $@

$(BUILD_DIR)/%.html: $(PAGES_DIR)/%.html | $(BUILD_DIR)
	bin/render $< > $@

static:
	@echo $(STATIC_SOURCES)

.PHONY: all
all: $(BUILD_TARGETS) $(STATIC_SOURCES)
	cp -r $(STATIC_DIR) $(BUILD_DIR)/static

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
