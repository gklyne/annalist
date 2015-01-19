/*
 * Adjust size attribute on elements with small-size-x, medium-size-x, etc class. 
 */

annalist = {

    resize_handler: function (event) {
        if (window.matchMedia(Foundation.media_queries['small']).matches)
        {
            $(".small-size-4").attr("size", 4);
            $(".small-rows-4").attr("rows", 4);
            /* $(".small-only-text-right").attr("text-align", "right"); doesn't work */
            $(".medium-add-margin").attr("width", "100%")
        };
        if (window.matchMedia(Foundation.media_queries['medium']).matches)
        {
            $(".medium-size-8").attr("size", 8);
            $(".medium-rows-8").attr("rows", 8);
            $(".medium-size-12").attr("size", 12);
            $(".medium-rows-12").attr("rows", 12);
            $(".medium-add-margin").attr("width", "95%")
        };
    }
};

$(window).resize(Foundation.utils.throttle(annalist.resize_handler, 10));

$(document).ready( function ()
{
    /* For new of copy operations, select the entity_id field */
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
});
