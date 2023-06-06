var map, marker1, marker2;
var isFirstPointSelected = false;

function initMap() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var initialLatlng = {lat: position.coords.latitude, lng: position.coords.longitude};
            document.getElementById('departure-input').value = position.coords.latitude + ',' + position.coords.longitude;

            map = new google.maps.Map(document.getElementById('map'), {
                center: initialLatlng,
                zoom: 15
            });

            marker1 = new google.maps.Marker({
                position: initialLatlng,
                map: map,
                title: 'Point 1',
                icon: {
                    url: 'http://maps.google.com/mapfiles/ms/icons/pink-dot.png'
                }
            });

            map.addListener('rightclick', function(e) {
                document.getElementById('departure-input').value = e.latLng.lat() + ',' + e.latLng.lng();
                marker1.setPosition(e.latLng);
            });

            map.addListener('click', function(e) {
                document.getElementById('arrival-input').value = e.latLng.lat() + ',' + e.latLng.lng();
                if (!marker2) {
                    marker2 = new google.maps.Marker({
                        position: e.latLng,
                        map: map,
                        title: 'Point 2'
                    });
                } else {
                    marker2.setPosition(e.latLng);
                }
                // Set the form fields to the new coordinates
                var coordinates1Field = document.getElementById('departure-input');
                var coordinates2Field = document.getElementById('arrival-input');
                coordinates1Field.value = marker1.getPosition().lat() + ',' + marker1.getPosition().lng();
                coordinates2Field.value = marker2.getPosition().lat() + ',' + marker2.getPosition().lng();
            });

            const trafficLayer = new google.maps.TrafficLayer();
            trafficLayer.setMap(map);
        }, function() {
            alert('Error: The Geolocation service failed.');
        });
    } else {
        alert('Error: Your browser doesn\'t support geolocation.');
    }
}
