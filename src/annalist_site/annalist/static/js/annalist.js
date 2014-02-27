/*
 * Adjust size attribute on elements with small-size-x, medium-size-x, etc class. 
 */

annalist = {

    resize_handler: function (event) {
        if (window.matchMedia(Foundation.media_queries['small']).matches){
            $(".small-size-4").attr("size", 4);
        };
        if (window.matchMedia(Foundation.media_queries['medium']).matches){
            $(".medium-size-8").attr("size", 8);
        };
    }
};

$(window).resize(Foundation.utils.throttle(annalist.resize_handler, 10));
