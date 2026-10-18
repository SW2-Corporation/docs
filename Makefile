# Compila documenti, lettere, verbali e presentazioni in build/ (Typst 0.15).
# La radice è la cartella del repo: i percorsi che iniziano con "/" partono da qui.
.RECIPEPREFIX = >
TYPST  ?= typst
PYTHON ?= python

DOC  := $(wildcard documenti/*/*.typ documenti/*/*/*.typ)
VERB := $(wildcard documenti/verbali/*/*.toml)
PRES := $(wildcard presentazioni/*.typ presentazioni/*/*.typ)
PDF  := $(DOC:%.typ=build/%.pdf) $(VERB:%.toml=build/%.pdf) $(PRES:%.typ=build/%.pdf)
DEPS := $(wildcard modello/*.typ dati/* assets/* documenti/*/*.csv documenti/*/*/*.csv)

all: $(PDF)

build/%.pdf: %.typ $(DEPS)
> @mkdir -p $(@D)
> $(TYPST) compile --root . $< $@

# i verbali sono dati TOML resi da modello/verbale.typ
build/%.pdf: %.toml $(DEPS)
> @mkdir -p $(@D)
> $(TYPST) compile --root . modello/verbale.typ $@ --input dati=$<

verifica:
> $(PYTHON) strumenti/verifica.py

test:
> $(PYTHON) -m unittest discover -s strumenti

sito:
> $(PYTHON) strumenti/sito.py --out build/site --typst $(TYPST)

# Ricompila al salvataggio: make watch F=documenti/interni/norme-di-progetto.typ
# (anche un verbale: make watch F=documenti/verbali/interni/AAAA-MM-GG.toml)
watch:
> @mkdir -p $(dir build/$(F))
ifeq ($(suffix $(F)),.toml)
> $(TYPST) watch --root . modello/verbale.typ build/$(F:.toml=.pdf) --input dati=$(F)
else
> $(TYPST) watch --root . $(F) build/$(F:.typ=.pdf)
endif

clean:
> rm -rf build

.PHONY: all verifica test sito watch clean
