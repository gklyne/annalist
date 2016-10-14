/*
 *  Javascript here provides some display enhancements when Javascript is available.
 *  The general idea is that the Javascript is not required, and default behaviour
 *  is still functional.
 */

annalist = {

    resize_handler: function (event) {
        /*
         *  Adjust sizing of selected controls when window is resized.
         */
        if (window.matchMedia(Foundation.media_queries['small']).matches)
        {
            $(".small-size-4").attr("size", 4);
            $(".small-rows-4").attr("rows", 4);
            /* $(".small-only-text-right").attr("text-align", "right"); doesn't work */
            $(".medium-add-margin").attr("width", "100%")
            $(".medium-up-text-right").removeClass("text-right");
        }
        else
        {
            $(".medium-up-text-right").addClass("text-right");
        };
        if (window.matchMedia(Foundation.media_queries['medium']).matches)
        {
            $(".medium-size-8").attr("size", 8);
            $(".medium-rows-8").attr("rows", 8);
            $(".medium-size-12").attr("size", 12);
            $(".medium-rows-12").attr("rows", 12);
            $(".medium-add-margin").attr("width", "95%")
        };
    },

    select_button_change: function (event) {
        /*
         *  Select character to display in button based on whether or not
         *  a value is selected: "+" if there is no selection, which causes
         *  a view to be created to define a new value, or "writing hand"
         *  (u+270D) for editing the selected value.
         */
        var div = event.data
        var sel = div.find("select");
        var val = sel.val();
        var btn = div.find("div.view-value.new-button > button > span.select-edit-button-text");
        /*
        if (window.console) {
            console.log("select_button_change");
            console.log("sel: "+sel.html());
            console.log("btn: "+btn.html());
            console.log("val: "+val);
        }
        */
        if (typeof btn !== "undefined") {
            btn.text(val ? "\u270D" : "+");
        }
    },

    select_button_init: function (index) {
        /*
         *  Initialize logic for selection new/edit button
         */
        var div = $(this);
        var sel = div.find("select");
        sel.on("change", div, annalist.select_button_change);
        sel.trigger("change");
    }

};

$(window).resize(Foundation.utils.throttle(annalist.resize_handler, 10));

$(document).ready( function ()
{
    /* For new or copy operations, select the entity_id field */
    /* console.log("annalist.js ready") */
    var e = $("input[type='hidden'][name='action']"); 
    if (e.length) 
    {
        var newactions = ["new", "copy"]
        if (newactions.indexOf(e.attr("value")) >= 0)
        {
            $("input[name='entity_id']").focus().select()
        }
    }
    /* For add/edit buttons on select widget, choose symbol based on state */
    $("div.view-value > select").parent().parent()
                                .has("div.view-value.new-button")
                                .each(annalist.select_button_init);
});

