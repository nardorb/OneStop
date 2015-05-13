window.onload = function(){

	// var = latt;
	// var = lng;
	var x = document.getElementById('test');
	x.innerHTML += "Gaza";

	// function getLocation(){
	// 	if (navigator.geolocation) {
	// 	        navigator.geolocation.getCurrentPosition(showPosition);
	// 	    } else {
	// 	        x.innerHTML = "Geolocation is not supported by this browser.";
	// 	    }
	// 	}
	// 	function showPosition(position) {
	// 	    x.innerHTML = "Latitude: " + position.coords.latitude + 
	// 	    "<br>Longitude: " + position.coords.longitude;
	// }

	var mapOptions = {
	    center: new google.maps.LatLng(37.7831,-122.4039),
	    zoom: 12,
	    mapTypeId: google.maps.MapTypeId.ROADMAP
	};

	new google.maps.Map(document.getElementById('map'), mapOptions);

	document.getElementById('test').style.color='red';
}

