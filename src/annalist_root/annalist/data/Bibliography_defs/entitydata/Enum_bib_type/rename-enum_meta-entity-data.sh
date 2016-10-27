# Rename enum_meta.jsonld files to entity_data.jsonld

files=$(find . -name enum_meta.jsonld -print)
# echo "@@ $files"

for src in $files; do
    # echo "@@ test $src"
    tgt=${src%enum_meta.jsonld}entity_data.jsonld
    echo "renaming $src -> $tgt"
    # mv $src $tgt
done

# End.
