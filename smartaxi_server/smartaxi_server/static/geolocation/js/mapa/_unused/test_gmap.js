// geo-point data model
var Point = Backbone.Model.extend({
    // explicitly specifiy the model
    defaults: {
        lat: 0.0,
        lng: 0.0,
        label: null
    },

    // convenience function
    toGPoint: function() {
        return new google.maps.LatLng(this.get('lat'), this.get('lng'));
    }
});

// collection of points
var Points = Backbone.Collection.extend({
    model: Point
});


//model is a composit model of points
var MapModel = Backbone.Model.extend({
    // by default models can't be nested
    initialize: function(opts) {
        Backbone.Model.prototype.initialize.apply(this, arguments);

        this.points = new Points;
        this.center = opts.center;
        // route changes to model listeners
        var self = this;

        this.points.on('add', function(newPoint) {
            self.trigger('points:add', newPoint);
        });

        this.points.on('remove', function(removedPoint) {
            self.trigger('points:remove', removedPoint);
        });

        this.points.on('reset', function(newPoints) {
            self.trigger('points:reset', newPoints);
        })

        this.center.on('change', function(newCenter) {
            self.trigger('center:change', newCenter);
        });

    },

    defaults: {
        label: null
    }
});

var GPointView = Backbone.View.extend({
    el: $('#mapCanvas'),

    initialize: function(opts) {
        this.model = opts.model;
        this.gmap = opts.gmap;

        var self = this;
        // update the position when the point changes
        this.model.on('change', function(updatedPoint) {
            self.gMarker.setPosition(updatedPoint.toGPoint());
        });
        // render the initial point state
        this.render();
    },

    render: function() {
        this.gMarker = new google.maps.Marker({
            position: this.model.toGPoint(),
            map: this.gmap,
            title: this.model.get('label')
        });
    },

    remove: function() {
        this.gMarker.setMap(null);
        this.gMarker = null;
    }
});


// GMapView
// anytime the points change or the center changes
// we update the model two way <-->
var GMapView = Backbone.View.extend({
    el: $('#mapCanvas'),

    initialize: function(opts) {
        // watch for point changes
        this.mapModel = opts.model;
        this.pointsToViews = {};


        var mapOptions = {
            zoom: 9,
            center: this.mapModel.center.toGPoint(),
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };

        this.gmap = new google.maps.Map(document.getElementById('mapCanvas'), mapOptions);

        // map the points to markers
        // attach to the map
        var self = this;
        this.mapModel.on('points:add', function(newPoint) {
            // convert added point to new marker
            self.pointsToViews[newPoint.cid] = new GPointView({
                model: newPoint,
                gmap: self.gmap
            });
        });

        this.mapModel.on('points:remove', function(removedPoint) {
            // map the model remove to a Marker remove
            var targetView = self.pointsToMarkers[removedPoint.cid];
            targetView.remove();
            delete self.pointsToViews[removedPoint.cid];
        });

        this.mapModel.on('points:reset', function(newPoints) {
            // remove all the current points
            _.each(_.values(self.pointsToViews), function(pointView) {
                // remove all the map markers
                pointView.remove();
            });
            // empty the map
            for (var k in self.pointsToViews) {
                delete self.pointsToViews[k];
            }

            // gmap render all the new points
            newPoints.each(function(newPoint) {
                self.pointsToViews[newPoint.cid] = new GPointView({
                    model: newPoint,
                    gmap: self.gmap
                });
            });
        });
    },

    render: function() {}
});


// main
$(function() {

    // make the model
    var point = new Point({
        lat: -34.357,
        lng: 151.1
    });

    var pointArray = [];

    for (var i = 0; i < 10; i++) {
        pointArray.push(new Point({
            lat: -34.397,
            lng: 150.644 + (i * 0.1)
        }));
    }

    var mapModel = new MapModel({
        center: point
    });

    // create the view
    mapView = new GMapView({
        model: mapModel
    });
    // goof around with the model
    mapModel.points.reset(pointArray);


    // pins fly like arrows
    var doc = $(document);
    var container = $('#mapCanvas');

    var mouseMove = doc.bindAsObservable('mousemove');

    var mouseMoveOffset = mouseMove.select(function(value) {
        var offset = container.offset();
        return {
            offsetX: value.clientX - offset.left + doc.scrollLeft(),
            offsetY: value.clientY - offset.top + doc.scrollTop()
        };
    });


    // store the original point vals
    var originalPointVals = [];
    _.each(pointArray, function(point) {
        originalPointVals.push({
            lat: point.get('lat'),
            lng: point.get('lng')
        });
    });

    mouseMoveOffset.delay(100).subscribe(function(mouseEvent) {
        for (var i = 0; i < pointArray.length; i++) {
            pointArray[i].set('lat', (mouseEvent.offsetY / 2000) + ((i * mouseEvent.offsetX) / 20000) + originalPointVals[i].lat);
            pointArray[i].set('lng', (mouseEvent.offsetX / 2000) + originalPointVals[i].lng);
        }
    });
})