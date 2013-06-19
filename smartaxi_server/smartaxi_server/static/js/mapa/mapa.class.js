/**
 * Created with PyCharm.
 * User: phantomis
 * Date: 15-06-13
 * Time: 21:38
 * To change this template use File | Settings | File Templates.
 */
(function (window, undefined) {

    var Mapa = (function () {

        // Config
        var config = {
            refreshRate: 600000 // 10 minutos
        };

        var mGeocoder;
        var mMap;
        var mMarkerClient;

        var mMapDomString = "map-canvas";
        var mMapDom = document.getElementById(mMapDomString);

        // Ambito privado
        var privado = {

            // Init
            init: function () {


                privado.initiateMap();
            },

            initiateMap: function () {
                console.log("initiating");
                mGeocoder = new google.maps.Geocoder();
                var myOptions = {
                    center: new google.maps.LatLng(-33.0352813, -71.5956843),
                    zoom: 8,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                };
                mMap = new google.maps.Map(jQuery("#map-canvas"), myOptions);

                mMarkerClient = new google.maps.Marker({
                    map: mMap,
                    position: new google.maps.LatLng(-33.0352813, -71.5956843),
                    draggable: true
                });
                google.maps.event.addListener(mMarkerClient, 'dragend', function () {
                    mGeocoder.geocode({'latLng': mMarkerClient.getPosition()}, function (results, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            if (results[0]) {
                                privado.setAddress(results[0]);
                                privado.cleanAdressList();
                            } else {
                                alert('No results found');
                            }
                        } else {
                            alert('Geocoder failed due to: ' + status);
                        }
                    });
                });
            },

            drawTaxi: function (taxi) {
                var contentString = "<p>Titulo</p>" + '<p> Speed: ' + taxi.speed + '</p>';
                var infowindow = new google.maps.InfoWindow({
                    content: contentString,
                    maxWidth: 100
                });
                var myLatlng = new google.maps.LatLng(taxi.latitude, taxi.longitude);
                var marker = new google.maps.Marker({
                    position: myLatlng,
                    map: mMap,
                    animation: google.maps.Animation.DROP,
                    icon: STATIC_URL + 'img/taxi_ico.png'
                });
                google.maps.event.addListener(marker, 'click', function () {
                    infowindow.open(mMap, marker);
                });
            },

            cleanAdressList: function () {
                $("#location_box").hide()
                $("#location_box").find("#location_results").empty();
            },

            setAddress: function () {
                $("#client_address").val(address.formatted_address)
                    .attr("data-latitude", address.geometry.location.jb)
                    .attr("data-longitude", address.geometry.location.kb);
                ;
                mapaObject.setCenter(address.geometry.location);
                mapaObject.setZoom(15);
                markerClient.setPosition(address.geometry.location);

                enableSaveClient();
            },


            // Procesos y manipulacion de data
            process: {


                address: {
                    molde: function () {
                        $("#client_address").val(address.formatted_address)
                            .attr("data-latitude", address.geometry.location.jb)
                            .attr("data-longitude", address.geometry.location.kb);
                        ;
                        mapaObject.setCenter(address.geometry.location);
                        mapaObject.setZoom(15);
                        markerClient.setPosition(address.geometry.location);
                    }
                },

                // Ultimos programas
                ultimosProgramas: {
                    refresh: function (programas) {

                    },
                    molde: function (programa) {

                    },

                    eventualizaCarrusel: function () {

                    }
                },

                // Programacion por dia
                programacionPorDia: {
                    refresh: function (data) {

                    },
                    molde: function (programa) {

                    },
                    actualizarSelectorDias: function (dias) {

                    }
                }
            }
        };

        // Ambito publico
        return {
            init: function () {
                privado.init();
            }
        };
    })();

    window.Mapa = Mapa;
})(window);

