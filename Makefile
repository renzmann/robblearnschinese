SRCDIR = src
BUILDDIR = build
PAGES_DIR = $(SRCDIR)/pages
HTML_SOURCES := $(wildcard $(PAGES_DIR)/*.html)
BUILD_TARGETS := $(patsubst $(PAGES_DIR)/%.html,$(BUILDDIR)/%.html,$(HTML_SOURCES))

$(BUILDDIR): $(SRCDIR)/CNAME $(SRCDIR)/**/*.html
	mkdir -p ./build
	cp CNAME $@

$(BUILDDIR)/%.html: $(SRCDIR)/pages/%.html | $(BUILDDIR)
	bin/render $< > $@

.PHONY: all
all: $(BUILD_TARGETS)

.PHONY: clean
clean:
	rm -rf $(BUILDDIR)/
