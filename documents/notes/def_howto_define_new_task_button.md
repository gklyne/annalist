# Adding a new task button to an edit view

## Add task button details to entity view

For built-in types, the file to edit is `annalist/data/sitedata/_view/<view_id>/view_meta.jsonld`.

The field `annal:edit_task_buttons` contains a list of task buttons that are displayed when editing.  Field `annal:view_task_buttons` lists task buttons displayed when viewing an entity.

Each entry in the list should contain the fields `annal:button_id`, `annal:button_label` and `annal:button_help`, shown this example, which is taken from `annalist/data/sitedata/_view/Type_view/view_meta.jsonld`:

	, "annal:edit_task_buttons":
	  [ { "annal:button_id":        "_task/Define_view_list" 
	    , "annal:button_label":     "Define view+list"
	    , "annal:button_help":      "Define initial view and list definitions for the current type.  (View and list type information and URI are taken from the current type; other fields are taken from the corresponding '_initial_values' record, and may be extended or modified later.)"
	    }
	  , ... (more button definitions)
	  ]

This should be sufficient for the new button to be displayed following reinstallation of the software and running `annalist_manager updatesitedata` before restarting the server (but clicking on the button will raise an error).

## Define logic for button activation

Currently, all task button functions are defined by python code in module `annalist/views/entityedit.py`, functions `find_task_button` and `save_invoke_task`.  Later, this logic is planned to be replaced by a data-driven form of action definition.

... (more) ...

