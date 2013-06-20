var Entities = {};
Entities.Views = {};
Entities.Models = {};
Entities.Collections = {};
//Backbone.sync = function(method, model) {
  //alert(method + ": " + model.url);
//};

Entities.Models.Point = Backbone.Model.extend({
	defaults: {
		latitude: 0.0,
		longitude: 0.0,
		resource_uri : null,
		session : null,
		speed : 0,
		timestamp: null
	},

    toGPoint: function() {
    	return new google.maps.LatLng(this.get('latitude'), this.get('longitude'));
    }
});

Entities.Collections.Points = Backbone.Collection.extend({
	model: Entities.Models.Point,
	url: function (){
		return '/api/v1/location/?format=json&limit=5&order_by=-id'
	},
	parse: function(resp, xhr) {
		//TODO: verificar que los datos son correctos
		return resp.objects;
	},
});


Entities.Views.markers = Backbone.View.extend({
	initialize: function () {
		var that = this;
		this.markersCollection = new Entities.Collections.Points();
		this.markersCollection.fetch({ 
			success: function (collection, response) {
				console.log(collection);
				_.each(collection.models,function(mark){
					var marker = new google.maps.Marker({
						map: map,
						position: mark.toGPoint(), 
						draggable: true
					});
				});
				//var variables = {markers: markers.models, _:_};
				//var template = _.template( $("#marker_template").html(), variables );
				//$(that.el).append(template);
			}
		});
	},
	render: function () {
		return this;
	},
});

Entities.Views.GMapView = Backbone.View.extend({
	el : $("#map-canvas"),
	initialize: function (opts){
		//this.mapModel = opts.model;
		var myOptions = {
			center: new google.maps.LatLng(-33.0352813,-71.5956843),
			zoom: 8,
			mapTypeId: google.maps.MapTypeId.ROADMAP
		};
		this.gmap = new google.maps.Map(document.getElementById("map-canvas"),myOptions);
	},
	render : function (){}
});

$(function () {

	// http://jsfiddle.net/rcastillo/JaNfQ/22/ MIRAR!!
	//var map_div = $(".map");
	//var myOptions = {
	//	center: new google.maps.LatLng(-33.0352813,-71.5956843),
	//	zoom: 8,
//		mapTypeId: google.maps.MapTypeId.ROADMAP
//	};
//	map = new google.maps.Map(map_div[0],myOptions);
//	var markers_view = new Entities.Views.markers({ el: map_div});
	var GMapView = new Entities.Views.GMapView({});
});
