require(['ext/jquery.min', 'ext/underscore.min', 'ext/backbone.min', 'template', 'locations'], function() {
    $(document).ready(function() {
        window.App = new LocationApp({ appendTo: $('#location') });
    });
});