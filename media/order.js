var directionsDisplay;
var directionsService = new google.maps.DirectionsService();
var map;


function initialize() {

	$("#autocomp").submit(function(){//alert(2);
		if ($("origin").val() != ''){
			return true;
		}{
			return false
		}
	});
	directionsDisplay = new google.maps.DirectionsRenderer();

	//-------------------------------------------------
	//create map
	//-------------------------------------------------
	var mapOptions = {
		// mapTypeId: google.maps.MapTypeId.ROADMAP,
		zoom: 17
	};
	map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
	directionsDisplay.setMap(map);

	//-------------------------------------------------
	// Geolocation Success
	//-------------------------------------------------
	// Try HTML5 geolocation

	if(navigator.geolocation) {
	navigator.geolocation.getCurrentPosition(function(position) {
	  var accuracy = position.coords.accuracy;
	  var pos = new google.maps.LatLng(position.coords.latitude,
	                                   position.coords.longitude);

	  //-------------------------------------------------
	  // Auto Complete
	  //-------------------------------------------------
	  var acOptions = {
	  	componentRestrictions: {country: 'jm'}
	  };

	  var autocomplete = new google.maps.places.Autocomplete(document.getElementById('autocomplete'),acOptions);
	  autocomplete.bindTo('bounds',map);
	  var infoWindow = new google.maps.InfoWindow();
	  var marker = new google.maps.Marker({
	    map: map
	  });

	  google.maps.event.addListener(autocomplete, 'place_changed', function() {
	    infoWindow.close();
	    var place = autocomplete.getPlace();
	    if (place.geometry.viewport) {
	      map.fitBounds(place.geometry.viewport);
	    } else {
	      map.setCenter(place.geometry.location);
	      map.setZoom(17);
	    }
	    marker.setPosition(place.geometry.location);
	    infoWindow.setContent('<div><strong>' + place.name + '</strong><br>');

	    infoWindow.open(map, marker);

	    google.maps.event.addListener(marker,'click',function(e){

	      infoWindow.open(map, marker);

	    });
	    calcRoute();
	    calculateDistances();
	  });

	  //-------------------------------------------------
	  // Directions
	  //-------------------------------------------------
	 var calcRoute = function () {//alert();
		var start = pos;
		var end = $("#autocomplete").val();
		var request = {
			origin:start,
			destination:end,
			travelMode: google.maps.TravelMode.DRIVING
		};
		directionsService.route(request, function(response, status) {
			if (status == google.maps.DirectionsStatus.OK) {
				directionsDisplay.setDirections(response);
			}
		});
	}

		//-------------------------------------------------
		// Distance
		//-------------------------------------------------
	 var calculateDistances = function() {
			var start = pos;
			var end = $("#autocomplete").val();
			var service = new google.maps.DistanceMatrixService();
			service.getDistanceMatrix(
			    {
			      origins: [start],
			      destinations: [end],
			      travelMode: google.maps.TravelMode.DRIVING,
			      unitSystem: google.maps.UnitSystem.METRIC
			    }, callback);
		}

		var callback = function(response, status) {
		  if (status != google.maps.DistanceMatrixStatus.OK) {
		    alert('Error was: ' + status);
		  } else {
		    var origins = response.originAddresses;
		    var destinations = response.destinationAddresses;
		    var outputDiv = document.getElementById("outputDiv");
		    document.getElementById("outputDiv").innerHTML = '';
		    // deleteOverlays();

		    for (var i = 0; i < origins.length; i++) {
		      var results = response.rows[i].elements;
		      for (var j = 0; j < results.length; j++) {
		        document.getElementById("outputDiv").innerHTML += origins[i] + ' to <br>' + destinations[j]
		            + ': <br> ' + results[j].distance.text + ' in <br>'
		            + results[j].duration.text + '<br>';
		        document.getElementById("origin").value += origins[i];
		      }
		    }
		  }
		}


	  var marker = new google.maps.Marker({
	        position: pos,
	        map: map,
	        title: 'There you are!'
	    });

	  var infoWindowOptions = {
	      content: 'We found you!'
	  };

	  var infoWindow = new google.maps.InfoWindow(infoWindowOptions);

	  google.maps.event.addListener(marker,'click',function(e){

	    infoWindow.open(map, marker);
	  });

	  map.setCenter(pos);



	}, function() {
	  handleNoGeolocation(true);
	}, {maximumAge:60000, timeout:5000, enableHighAccuracy:true});
	} else {
	// Browser doesn't support Geolocation
	handleNoGeolocation(false);
	}
}

//-------------------------------------------------
// Geolocation Failure
//-------------------------------------------------

function handleNoGeolocation(errorFlag) {

	if (errorFlag) {
		var content = 'Error: The Geolocation service failed.';
	} else {
		var content = 'Error: Your browser doesn\'t support geolocation.';
	}

	var options = {
		map: map,
		position: new google.maps.LatLng(60, 105),
		content: content
	};

	var marker = new google.maps.Marker(options);
	map.setCenter(options.position);

	var infoWindowOptions = {
	  content: 'We couldn\'t find you'
	};

	var infoWindow = new google.maps.InfoWindow(infoWindowOptions);
	google.maps.event.addListener(marker,'click',function(e){

		infoWindow.open(map, marker);

	});
}


google.maps.event.addDomListener(window, 'load', initialize);