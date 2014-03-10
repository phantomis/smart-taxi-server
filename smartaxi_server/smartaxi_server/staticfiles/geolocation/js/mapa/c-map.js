$(document).ready(function () {

    var geocoder
    var mapaObject
    var markerClient
    var circle
    var markersArray = [];
    var taxis = {}

    var taxiDrawerInterval;

    var taxiStatus = {
        "1": "Disponible",
        "2": "No Disponible",
        "3": "Ausente",
        "4": "En Carrera"
    }

    var general_latitude = ""
    var general_longitude = ""

    $("#dialog").dialog({
        modal: true,
        dialogClass: "no-close",
        autoOpen: false,
        width: 400

    });

    initialize();
    showTaxis();


    taxiDrawerInterval = setInterval(function () {
        showTaxis()
    }, 5000);

    function initialize() {
        geocoder = new google.maps.Geocoder();
        var myOptions = {
            center: new google.maps.LatLng(-33.0352813, -71.5956843),
            zoom: 8,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        mapaObject = new google.maps.Map(document.getElementById("map-canvas"), myOptions);
        if (google.loader.ClientLocation) {
            var center = new google.maps.LatLng(
                google.loader.ClientLocation.latitude,
                google.loader.ClientLocation.longitude
            );
            mapaObject.setCenter(center);
        }
        markerClient = new google.maps.Marker({
            map: mapaObject,
            position: new google.maps.LatLng(-33.0352813, -71.5956843),
            draggable: true
        });
        google.maps.event.addListener(markerClient, 'dragend', function () {
            console.log(markerClient.getPosition());
            geocoder.geocode({'latLng': markerClient.getPosition()}, function (results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    if (results[0]) {
                        setAddress(results[0]);
                        cleanAdressList();
                    } else {
                        alert('No results found');
                    }
                } else {
                    alert('Geocoder failed due to: ' + status);
                }
            });
        });
        $(window).resize(function () {
            var h = $(window).height(),
                offsetTop = 200; // Calculate the top offset
            $('#map-canvas').css('height', (h - offsetTop));
        }).resize();
    }

    function showTaxis() {
        clearOverlays();
        clearTable();
        $.ajax({
            type: 'GET',
            url: "/api/v1/mapa/?only_lasts=true",
            dataType: "json",
            processData: false,
            contentType: "application/json",
            success: function (result) {
                if (result.objects) {
                    taxis = result.objects
                    $.each(result.objects, function (index, value) {
                        drawTaxi(value);
                        addTaxiToTable(value);
                    })
                }
            }
        });
    }

    function addTaxiToTable(location) {

        var s = location.user.taxi.status;
        var rowClass = "class=' ";
        if (s == "1") {
            rowClass += "success";
        } else if (s == "2") {
            rowClass += "error";
        } else if (s == "3") {
            rowClass += "info";
        } else if (s == "4") {
            rowClass += "warning";
        }

        var taxiTime = new Date(location.timestamp);
        var umbralTime = new Date(new Date().getTime() - 9*30*60000);

        if(taxiTime < umbralTime){
            rowClass += " isOld";
        }

        rowClass += "'";
        var row = "<tr " + rowClass + ">" +
            "<td>" + location.user.taxi.id + "</td>" +
            "<td>" + location.user.taxi.license_plate + "</td>" +
            "<td>" + taxiStatus[location.user.taxi.status] + "</td>" +
            "</tr>";
        $('#taxis-table tbody').append(row);
    }

    function drawTaxi(value) {
        //var contentString = "<p>" + value.user.taxi.license_plate + "</p>" + '<p> Speed: ' + value.speed + '</p>';
        var contentString =
            "<p>" +
                "<strong> Patente: </strong> " + value.user.taxi.license_plate + " <br/>  " +
                "<strong> Velocidad: </strong>" + value.speed + " <br/> " +
                "<strong> Ultima vez visto: </strong>" + jQuery.timeago(value.timestamp) + "<br/> " +
                "<strong> Estado: </strong>" + taxiStatus[value.user.taxi.status] +
                "</p> ";

        var infowindow = new google.maps.InfoWindow({
            content: contentString,
            maxWidth: 100
        });
        var myLatlng = new google.maps.LatLng(value.latitude, value.longitude);
        var marker = new google.maps.Marker({
            position: myLatlng,
            map: mapaObject,
            title: "Hello World!",
            //animation: google.maps.Animation.DROP,
            icon: STATIC_URL + 'img/taxi_ico.png'
        });
        markersArray.push(marker);
        //infowindow.open(mapaObject, marker);
        google.maps.event.addListener(marker, 'click', function () {
            infowindow.open(mapaObject, marker);
        });
    }

    function clearOverlays() {
        for (var i = 0; i < markersArray.length; i++) {
            markersArray[i].setMap(null);
        }
        markersArray = [];
    }

    function clearTable() {
        $("#taxis-table > tbody").html("")
    }

    function cleanAdressList() {
        $("#location_box").hide()
        $("#location_box").find("#location_results").empty();
    }

    function codeAddress() {
        var address = $("#client_address").val();
        geocoder.geocode({ 'address': address}, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                console.log(results);
                if (results.length > 1) {
                    var results_container = $("#location_box");
                    results_container.show();
                    var location_results = results_container.find("#location_results");
                    location_results.empty();
                    $.each(results, function (index, value) {
                        var $item = $("<div class='alert alert-info'>" + value.formatted_address + "</div>")
                            .attr("data-latitude", value.geometry.location.jb)
                            .attr("data-longitude", value.geometry.location.kb);
                        $item.on("click", function (event) {
                            setAddress(value);
                        });
                        location_results.append($item);
                        disableSaveClient();
                    });
                } else {
                    setAddress(results[0]);
                    cleanAdressList();
                }


            } else {
                alert("Geocode was not successful for the following reason: " + status);
            }
        });
    }




    function setAddress(address) {
        $("#client_address").val(address.formatted_address)
            .attr("data-latitude", address.geometry.location.jb)
            .attr("data-longitude", address.geometry.location.kb);
        general_latitude = address.geometry.location.jb;
        general_longitude = address.geometry.location.kb;
        mapaObject.setCenter(address.geometry.location);
        mapaObject.setZoom(15);
        markerClient.setPosition(address.geometry.location);

        enableSaveClient();
    }


    function enableSaveClient() {
        if ($('input[id="client_name"]').val() && $('input[id="client_phone"]').val() && $('input[id="client_address"]').val()) {
            $("#get_near_taxis").removeAttr("disabled");
        }

    }

    function disableSaveClient() {
        $("#get_near_taxis").attr("disabled", "disabled");
        $("#send_location").attr("disabled", "disabled");
    }

    function addUser(userData, _fnCallback) {
        console.log(userData);
        $.ajax({
            type: 'POST',
            url: '/api/v1/client/',
            data: userData,
            dataType: "json",
            processData: false,
            contentType: "application/json",
            success: function (data, textStatus, jqXHR) {
                _fnCallback.success(data)
            },
            error: function (jqXHR, textStatus, errorThrown) {
                _fnCallback.error(textStatus);
            }
        });
    }


    //Eventos

    $("#send_location").on("click", function (event) {
        clearInterval(taxiDrawerInterval);
        //var lat = $("#client_address").attr("data-latitude");
        //var lon = $("#client_address").attr("data-longitude");
        var userData = {
            "name": $("#client_name").val(),
            "phone_number": $("#client_phone").val(),
            "location": {
                "address_name": $("#client_address").val(),
                "latitude": general_latitude,
                "longitude": general_longitude
            }
        }

        addUser(JSON.stringify(userData), {
            success: function (client) {

                $.each(taxis, function (index, taxi) {
                    if (taxi.user.taxi.status == "1") {
                        sendLocation(taxi.user.taxi.id, client.id);
                    }
                })
                searchTravelAccepted(client.id)
                $("#dialog").dialog("open");
            },
            error: function (textStatus) {
                console.log(textStatus)
            }
        })


    });

    $("#search_location").on("click", function (event) {
        codeAddress();
    });

    $("#get_near_taxis").on("click", function (event) {
        clearInterval(taxiDrawerInterval)

        //var lat = $("#client_address").attr("data-latitude");
        //var lon = $("#client_address").attr("data-longitude");
        var r = $("#radious_map").val();
        drawCircle(general_latitude, general_longitude, r);
        general_latitude(general_latitude, general_longitude, r);
        mapaObject.fitBounds(circle.getBounds());
        taxiDrawerInterval = setInterval(function () {
            searchAndDrawNear(general_latitude, general_longitude, r);
        }, 3000);
        $("#send_location").removeAttr("disabled");
    });

    function searchAndDrawNear(lat, lon, r) {
        searchNearPoint(lat, lon, r, {
            onSucess: function (result) {
                clearOverlays()
                clearTable();
                if (result.objects) {
                    taxis = result.objects
                    $.each(result.objects, function (index, value) {
                        drawTaxi(value);
                        addTaxiToTable(value)
                    })
                }
            },
            onError: function (error) {
                console.log("error: " + error)
            }
        });
    }


    function searchNearPoint(lat, long, r, callback) {
        parameters = {
            lat: lat,
            long: long,
            r: r
        }
        console.log(parameters)
        $.ajax({
            type: 'GET',
            url: '/api/v1/mapa/search/?format=json',
            data: parameters,
            contentType: "application/json; charset=utf-8",
            success: function (data, textStatus, jqXHR) {
                callback.onSucess(data)
            },
            error: function (jqXHR, textStatus, errorThrown) {
                callback.onError()
            }
        });
    }

    //cuando se completa el nombre y el telefono , se habilita el boton guardar (previa revision de la direccion)
    $('input[id="client_name"],input[id="client_phone"]').keypress(function () {
        enableSaveClient();
    });

    //Cuando se escribe a mano, se deshabilita el "guardar"
    $('input[id="client_address"]').keypress(function () {
        disableSaveClient();
    })
        .on("click", function () {
            disableSaveClient();
        });

    $('html').keyup(function (e) {

        if (e.keyCode == 13)codeAddress();
    });

    function drawCircle(lat, lng, rad) {

        rad *= 1000; // convert to meters if in kms
        if (circle != null) {
            circle.setMap(null);
        }
        circle = new google.maps.Circle({
            center: new google.maps.LatLng(lat, lng),
            radius: rad,
            strokeColor: "#FF0000",
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: "#FF0000",
            fillOpacity: 0.35,
            map: mapaObject
        });


    }

    function sendLocation(taxiId, clientId) {
        var parameters = JSON.stringify({
            "taxi": "/api/v1/taxi/" + taxiId + "/",
            "client": "/api/v1/client/" + clientId + "/"
        });
        console.log(parameters)
        $.ajax({
            type: 'POST',
            url: '/api/v1/travel/',
            data: parameters,
            dataType: 'json',
            processData: false,
            contentType: "application/json; charset=utf-8",
            success: function (data, textStatus, jqXHR) {
                console.log(data)
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(textStatus)
            }
        });
    }

    function searchTravelAccepted(idClient) {
        clearOverlays();
        clearTable();
        var success = false;
        $.ajax({
            type: 'GET',
            url: "/api/v1/travel/?client=" + idClient,
            dataType: "json",
            processData: false,
            contentType: "application/json",
            success: function (result) {
                if (result.objects) {
                    travels = result.objects
                    $.each(travels, function (index, travel) {
                        if (travel.status == "3") {
                            $("#dialog").dialog("close");
                            alert("Se agendó correctamente el viaje al taxi");
                            resetAll();
                            success = true;
                            return;
                        }
                    })
                    if (!success) {
                        setTimeout(function () {
                            searchTravelAccepted(idClient);
                        }, 2000)
                    }
                }
            }
        });
    }

    function resetAll() {
        document.location.reload(true);
    }

});
