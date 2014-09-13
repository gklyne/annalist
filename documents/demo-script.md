# Simple demonstration/evaluation script

## First demo: simple musical instrument catalogue

@@Just rough notes so far@@

Create collection: MusicalInstruments

Click on collection link

Click 'new'.  Enter details: id, label, comment.

Click 'add field': (view description displayed - note new "Default_field" at bottom)

Click 'New field'

Enter id (InstrumentType), label, help, placeholder, property, size/position

Click 'Save'

In new "Default field", click dropdown and select InstrumentType ***'Select' label is not useful -- suggest 'Field type' ***

Enter size/position information as "small:0,12"

Click 'Save'.  Note that we have returned to the original with details about as guitar, but a new field is displayed.  Enter "string" in the new field.

Click 'Save'

We now see a list of entities: the guitar, and two records for the instrument type field and a "Default_view".  But now the Default_view is mis-named:  select the checkbox and click on 'Edit'

Change the id to "Instrument_view", and update the label and help text.

Click 'Save':  see Id and label displayed are changed.

Click on 'guitar':  want to designate this is a musical instrument.

Note that the instrument view is not displayed.  From the 'Choose view' dropdown, select "Instrument_view", and click 'Show view'.

Click 'New type'.  Enter details.  Select 'Default view' is "Instrument_view".  Leave 'Default list' for now.

Click 'Save' -> back to guitar record.

Select "MusicalInstrument" from 'Type' dropdown.

Click 'Save'.  Note a new 'Type' is displayed, and the Type of guitar displayed as "MusicalInstrument"

Click on 'guitar', note that it displays straight away in 'Instrument_view'

Click 'Cancel'.

Create another instrument record: click 'New'.

Under 'Choose view', select "Instrument_view" and click 'Show view'.

Enter details, including type as "MusicalInstrument"

So far, we have used "Default_list_all" to display the listb of entities, which includes internal details we don't normally want to see.  Click 'Customize'.

Under 'List views' click 'New'.

Fill in details, keeping the default field descriptions, and click 'Save'.  The selector field restricts the type of records that are displayed (cf. URI in MusicalInstrumemnt type)

Click 'Close' to return to the list display.  See the new "Instrument_list" is now shown.

From 'List view' select "Instrument_list", and click 'view'.

To add information to the list, click 'Customize' again.

Select "Instrument_list" and click the 'Edit' button below.

Select the "Entity_label" checkbox and click 'Remove selected field(s)'.

Click 'Add field'.

Select "InstrumentType" and enter "small:3,3" for the size/position value.

Click 'Add field' again.

Select "Entity_label" and enter "small:6,6" for the size/position value.

Click 'Save'

Click 'Close' - see the list display is updated to show the type of each instrument listed.

To make this the default list display for this collection, click 'Set default'.  Test this by clicking 'Close', then clicking again on "MusicalInstruments"

Note also that clicking on the 'New' button from this default initial display now takes you directly to the musical instrument view, whioch defaults to setting the entity type as "MusicalInstrument"

New fields can be added to the musical instrument view as needs arise.  (They won't be retrospectively populated in existing records, but the fields will appear whenever the view is displayed so additional details can be added when editing older records.


## Second demo:

Add musicians to catalogue, and cross-link

@@TODO





