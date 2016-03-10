# Status

The material in this directory is currently a draft


# Document preparation

The primary source files for the document are:

* Annalist-paper-ACMSIG.tex (document skeleton, with references to foirmatting style)
* Annalist-paper-body.tex (TeX document body content [[pwith final formatting edits applied by hand to PanDoc-generated TeX]])
* refs.bib
* figures/ subdirectory for figures in document

Preparation of the final PDF document uses a tool chain involving "pandoc", "bibtex" and "pdflatex".  Scripts used include

make-tex-from-md.sh
make-pdf-from-tex.sh



