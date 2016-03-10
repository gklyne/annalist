# Generate .aux
pdflatex Annalist-paper-main.tex
# Generate .bbl
bibtex Annalist-paper-main
# Page count
pdflatex Annalist-paper-main.tex
# Final formatting
pdflatex Annalist-paper-main.tex
# End.
