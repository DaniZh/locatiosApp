(function () {
    var TEMPLATE_URL = '/static';

    var Location = Backbone.Model.extend({

        defaults: function () {
            return {
                name: '',
                lat: '',
                lng: '',
                address: ''
            };
        }
    });

    var LocationList = Backbone.Collection.extend({

        model: Location,
        url: '/locations/',

        comparator: function (location) {
            return location.get('name');
        }

    });

    MapView = Backbone.View.extend({
            initialize: function () {
                markers = {};
                map = null;
                geocoder = new google.maps.Geocoder();
                var mapOptions = {
                    zoom: 4,
                    center: new google.maps.LatLng(-25.363882, 131.044922)
                };
                map = new google.maps.Map(document.getElementById('map-canvas'),
                    mapOptions);
            }
        }
    );

    var LocationView = Backbone.View.extend({

        tagName: "li",

        events: {
            "dblclick div.location-name": "edit",
            "click span.location-destroy": "clear",
            "keypress .location-input": "updateOnEnter"
        },

        initialize: function () {
            this.model.bind('change', this.render, this);
            this.model.bind('destroy', this.remove, this);
        },

        render: function () {
            var self = this;

            $(self.el).template(TEMPLATE_URL + '/templates/item.html', self.model.toJSON(), function () {
                self.setText();
                self.addMarker();
            });

            return self;
        },

        setText: function () {
            var name = this.model.get('name');
            var address = this.model.get('address');
            var lat = this.model.get('lat');
            var lng = this.model.get('lng');
            this.$('.location-name').text(name);
            this.$('.location-address').text(address);
            this.input = this.$('.location-input');
            this.input.bind('blur', _.bind(this.close, this)).val(name);
        },

        edit: function () {
            $(this.el).addClass("editing");
            this.input.focus();
        },

        close: function () {
            this.model.save({name: this.input.val()});
            $(this.el).removeClass("editing");
        },

        addMarker: function(){
               var lat = this.model.get('lat');
	           var lng = this.model.get('lng');
               markers[this.model.id] = this.placeMarker(null, map, lat, lng );
        },

         placeMarker: function(position, map, lat, lng) {
                if(!position){
                    position = new google.maps.LatLng(lat, lng);
                }
                return  new google.maps.Marker({
                    position: position,
                    map: map
                });
        },

        updateOnEnter: function (e) {
            if (e.keyCode === 13) {
                this.close();
            }
        },

        remove: function () {
            $(this.el).remove();
        },

        clear: function () {
            var marker = markers[this.model.id];
            if (typeof marker !== "undefined") {
            marker.setMap(null);
            }
            this.model.destroy();
        }

    });

    window.LocationApp = Backbone.View.extend({

            locations: new LocationList(),

            events: {

            },

            initialize: function (options) {
                this.map = new MapView;
                var self = this,
                parentElt = options.appendTo || $('body');

                TEMPLATE_URL = options.templateUrl || TEMPLATE_URL;

                parentElt.template(TEMPLATE_URL + '/templates/app.html', {}, function () {
                    self.el = $('#locationapp');
                    self.delegateEvents();

                    self.input = self.$("#new-location");

                    self.locations.bind('add', self.addOne, self);
                    self.locations.bind('reset', self.addAll, self);
                    self.locations.bind('all', self.render, self);
                    self.locations.fetch();
                });

                with ({ self: self }) {
                    google.maps.event.addListener(map, 'click', function (e) {
                        var latLng = e.latLng;
                        var lat = e.latLng.lat();
                        var lng = e.latLng.lng();
                        var latLng = e.latLng;
                        var address = "";
                        geocoder.geocode({'latLng': latLng}, function (results, status) {
                            if (status == google.maps.GeocoderStatus.OK) {
                                if (results[1]) {
                                    address = results[1].formatted_address;
                                    self.locations.create({name: "Enter note", lat: lat, lng: lng, address: address, done: false});
                                } else {
                                    alert('No results found');
                                }
                            } else {
                                alert('Geocoder failed due to: ' + status);
                            }
                        });
                    });
                }
            },

            render: function () {
                var self = this,
                    data = {
                        total: self.locations.length
                    };

                $('#location-stats').template(TEMPLATE_URL + '/templates/stats.html', data);

                return this;
            },

            addOne: function (location) {
                var view = new LocationView({model: location});
                $("#location-list").append(view.render().el);
            },

            addAll: function () {
                this.locations.each(this.addOne);
            }

        });

}());
