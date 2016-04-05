# Generate .aux
pdflatex Annalist-paper-ACMSIG.tex
# Generate .bbl
bibtex Annalist-paper-ACMSIG
# Final formatting
pdflatex Annalist-paper-ACMSIG.tex
# End.
