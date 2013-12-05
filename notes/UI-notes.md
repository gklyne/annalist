# Editing interface

Include (hide-able) fields for displaying orignal values.

When submitting changes, to eTag test - if mismatch, use original value fields to highlight fields whose values changed since the original edit, and conflicts with changes made locally.  This should ensure safe mukltiuser editing.  Also, set flag in data when starting an edit, clear when submitted.  If there is an outstanding edit less than (say) 1 day old, show a warning when starting new edit.

Keep note of most recent record entered for any type/view, and provide option to copy values to new record.

