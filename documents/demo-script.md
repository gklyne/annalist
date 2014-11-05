# Simple demonstration/evaluation scripts

The following introductory screencast vodeos can be downloaded from [annalist.net](http://annalist.net):

1. [Initializing Annalist site data](http://annalist.net/media/annalist-site-setup.mp4) (1m47s) - shows the procedure for first-time initialization of new Annalist site data using the `annalistr-manager` utility.
2. [Log in and and create first collection](http://annalist.net/media/annalist-login-create-collection.mp4) (3m32s) - 
3. [Initial entry of data in a new collection](http://annalist.net/media/annallist-create-configure-data-records.mp4) (3m32s) - 
4. [Configure types and record views in a data collection](http://annalist.net/media/annallist-configure-type-view-records.mp4) (3m46s)
5. [Configure list view and default display](http://annalist.net/media/annallist-configure-default-list-record.mp4) (3m51s)
6. [Using multiple record types](http://annalist.net/media/@@TODO.mp4) (@@TODO)

Scripts for the above demonstration sequences, to allow the seuqnce to be performed locally, can be found below.

The [original 6 minute demonstration screencast](http://annalist.net/media/orig-annalist-demo-music-instrument-catalogue.mp4) can also be downloaded, but this is based on earlier software and differs in several ways from the current software.


## Initializing Annalist site data

`annalist-site-setup.mp4` - (1m47s)

This demonstration sequence starts with a fresh Annalist software installation, configured to accept OpenId Connect user authentication from Google.  It covers use of the `annalist-manager` command line tool to initialize Annalist site data, create an initial administrative user, and specify default user permission data.

The sequence used here creates "personal" Annalist site data in the home directory of the currently logged-in user.

1. Create new Annalist site structure:

        annalist-manager createsite

2.  Initialize the web site management database:

        annalist-manager initialize

3.  Create an initial admin user (with user-id `admin`) with a supplied password:

        annalist-manager defaultadminuser

4.  Set default permissions to allow any logged-in user to create a new data collection:

        annalist-manager setdefaultpermissions "VIEW CREATE_COLLECTION"

5.  Start the Annalist web site server:

        annalist-manager runserver

With the Annalist server running, the next demo will show how to log in to the web site and create a first data collection.


## Log in and and create first collection

`annalist-login-create-collection.mp4` - (3m32s)

This demo provides a first view of the Annalist web site interface, and shows the initial steps followed to log in and create a data collection.  It starts with a running Annalist server and newly initialized site data and (see previous demo).  It also assumes the server is configured to accept OpenID Connect user credentials from Google.

1.  Start a web browser on the same computer that is running an Annalist server, and browse to [localhost:8000](http://localhost:8000).

2.  Select "Login" from the top menu bar, and  and Use the "Local user credentials" link to login as 'admin', using the password just given when initializing Annalist site data.

3.  Select "Home" from the top menu bar:  an empty list of data collections is presented, along with controls to create a new collection.

4.  Enter details for a new collection, and click "New".

5.  The new collection now shows in the list; click on the link to view the new collection.  A single record is shown for the `admin` user.

6.  Click on the `admin` user link, and note the permissions shown.  Whenever a new collection is created, the creator (in this case, user `admin`) is automatically given full permissions over that collection.

7.  Click "Cancel" to return to the collection default display.

8.  We will create a new non-admin user with full permissions over this new collection:  select `User_list` and click "View"

9.  Click "New"

10.  Enter details for a Google-authenticated user, click "Save".  The user id must match a value that will be used later for login, and the URI must be a mailto: URI matching the email address of the user's Google account.

11. Click "Close" to return to the site front page view (list of collections)

12. Click "Logout"

13. Click "Login", enter the local user id just created, and ensure "Google" is selected as the Login service.

12. Click "Login".  At this point, prompts may be issued to enter Google account and password details.  If the user is already logged in to Google, no further information is requested.

    Assuming the credentials are all good, Annalist login completes and brief information about the user is displayed.

13. Click "Home" in the top menu bar.  The list of collections is displayed again.

14. Click on the link for the new collection created just now.

15. Click on "New", and note that the new user has permissions to create and edit collection content.

This completes the demo.  The next demo will show population of a new collection with simple data records.


## Initial entry of data in a new collection

`annallist-create-configure-data-records.mp4` - (3m26s)

This demo creates a new collection and populates it with a couple of simple desctriptions of musical instruments.  It shows that new fields can be added to presented data records as needs are identified.

The demo sequence starts with an empty Annalist site, and a logged in user with permissions to create a new collection.

1. Create new collection "MusicalInstruments"

2. Clock on "MusicalInstruments" collection link to view the new collection

3. Click "New"

4. Enter values:

    Id: "guitar"

    Label: "Guitar (accoustic)"

    Comment: "String instrument with 6 strings, a fretted neck and a sound box."

5.  Next, we shall add a field indicating the class of instrument.  Click on 'New field'.

6.  Enter values:

    id: "InstrumentType"

    Field value type: "annal:Text"

    Field render type "Text"

    Label: "Instrument type"

    Description: "Keyword indicating broad class of instrument (e.g. string. wind, brass, etc.)"

    Placeholder: "(Type of instrument; e.g. string. wind, brass, etc.)"

    property: "micat:instrument_type"

    size/position: "small:0,12; medium:0,6"

    Leave remaining fields untouched.

7.  Click "Save".  The 'guitar' record is displayed again.

8. Click "Add field".  Towards the bottom of the page is a list of fields.  In the last entry, change values thus:

Field id: "InstrumentType"

Size/position: "small:0,12;medium:0,6"

9.  Click "Save".  The guitar record is redisplayed with a new field "Instrument type".  Enter "string" into this field.

10.  Click "Save".  The collection now shows new entries for "InstrumentType", "Default_view" and "guitar"

11. Click "New" again.

12. Enter:
    Id: "trumpet"
    Type: "Default_type"
    Label: "Trumpet"
    Comment: "Brass instrument with folded tube and three valves."
    Instrument type: "brass"

13. Click "Save".  Observe both "guitar" and "trumpet" appear in the list.

This concludes the demonstration of simple data entry and adding new fields to a data entry form.  In the next demo, we shall see how to customize the presentation of data in a collection to focus on the actual data it contains.


## Configure types and record views in a data collection

`annallist-configure-type-view-records.mp4` - (3m46s)

This sequence shows how a collection can be configured to reflect the data it contains, through the addition of customized types and record views.  It starts with the simple musical instruments catalogue created in the previous demonstration.

1.  View the Musical Instruments data collection.

    Note that the musical instruments are shows as "Default_type", and that other records present are described as "_field, "_user" and "_view" values.

2.  Click on "Customize"

    Columns are displayed for Record types, List views and Record views.  A single record view "Default_view" is shown.  (This was created previously when a new field was added to the default record view.)

    To customize the collection for musical instrument data, we shall create new a record type and rename Default_view to reflect its use to display musical instrument records.

3.  Click on "New" in the record types column.  Fill in the fields displayed:

    Id: MusicalInstrument

    Label: Musical instrument

    Comment: Record type for musical instrument description

    URI: micat:MusicalInstrument

    Click "Save", leaving remaining fields as they are for now.

4.  "MusicalInstrument" now appears in the record type column.

5.  In the Record views column, select `Default_view` and click on "edit"

6.  Change field values:

    Id: Instrument_view

    Label: Musical instrument view

    Help: View musical instrument description

    Record type: micat:MusicalInstrument

    Click "Save" leaving other fields unchanged.  Note that the Record views column now contains an entry `Instrument_view`.

7.  Clock "Close", then click on the link for `guitar`.

    Note that the view now does not displkay the instrument type field added previously.

    In the "Choose view" field select `Instrument_view`, then click "Show view".

    The instrument type is now shown.

8.  In the "Type" field select `MusicalInstrument` and click on "Save".

    The "Guitar" record now displays with type "MusicalInstrument".

9.  Click on "Customize" again.

    In the record types column select `MusicalInstrument` and click "Edit"

    In field "Default view" select `Instrument_view`, and click "Save".

    Click "Close" to return to the collection display.

10. Click on the `guitar` link.

    Note that it now displays by default with `Instrument_view`, showing the instrument type field.

    Click "Cancel"

11. Click on the `trumpet` link.

    Note that it shows as `Default_type` using `Default_view`.

    From the "Type" field, select `MusicalInstrument`, then click "Save".

12. Again, Click on the `trumpet` link.

    This time it displays as a `MusicalInstrument` using the `Instrument_view` form.

    Click "Cancel"

This demonstration has shown how the presentation of data records can be changed through the definition of customized types and views.  It also shows how these changes can be made _post hoc_:  existing data records and views can be updated to reflect changes to the data.

In practice, I would recommend to define an appropriate (non-default) type for data records before creating the data.  The record type is mainly a convenient label, and does not impose any structural constraints on the data.

The next demonstration will continue customizing the musical instruments catalogue to make data entry and display proceed more smoothly.


## Configure list view and default display

`annallist-configure-default-list-record.mp4` - (3m51s)

Starting with the customized musical instruments catalogue from the previous Annalist demonstration, this demonstration sequence shows how a collection can be further configured to reflect the data it contains through the addition of customized list views.


1.  View the Musical Instruments data collection.

    Following the previous demo, the `guitar` and `trumpet` records are shown as having type "MusicalInstrument".

    We shall proceed to create a customized list view for musical instruments.

2.  Click on "Customize"

3.  In the List views column, click on "New"

    Fill in the fields thus:

    Id: Instrument_list

    Label: Musical instrumemnts

    Help: Listing of musical instruments

    Record type: MusicalInstrument

    View: Instrument_view
    
    Selector: micat:MusicalInstrument in [@type]

    Record type URI: micat:MusicalInstrument

4.  Add an instrument type field to the listing

    Because there is currently no facility to reorder defined fields, we need to delete an existing field and redefine fields in the desired order.)

    Select the check box by Field id `Entity label`, then click on "Remove selected field(s)".

    Click on "Add field" and enter details "InstrumentType" and "small:3,3".

    Click on "Add field" again and enter details "Entity_label" and "small:6,6".

    Click "Save".

5.  Click "Close", returning to the main collection display.

6.  In field "List view" select `Instrument_list` and click "View"

    The display changes to a list of Musical instruments, with a column for instrument type.

7.  To make this display default for the collection, click on "Set default".

    To see the effect of this, click on "Home" inthe top menu bar, then on the "MusicalInstrument" collection link.

8.  To complete the customization, make the new list default for type "MusicalInstrument":

    Click on "Customize"

    In the Record type column, select `MusicalInstrument` and click on "Edit"

    In field "Default list" select `Instrument_list`, and click "Save"

    Click "Close"

9.  Create another musical instrument record:

    Click on "New:".  Note that the type is pre-selected as `MusicalInstrument`, and the view is `Instrument_view` (showing the instrument type field).

    Enter new values:

    Id: violin

    Label: Standard violin

    Comment: An instrument with 4 strings, a neck without frets and a sound box.

    Instrument type: string

    Click on "Save".

10. Home page

    Click on MusicalInstruments link

    Note that the display comes up with the customized list of musical instruments.


The musical instrument catalogue has now been customized to display a list of musical instruments as its default front-page display, and to use appropriate defaults when creating and displaying new data records.

The next demonstration will introduce a second record type into a collection, and show how links can be created between records.
 
----

## Next demo:

Add musicians to catalogue, and cross-link

@@TODO





