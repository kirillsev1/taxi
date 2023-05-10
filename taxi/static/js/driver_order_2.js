var map, marker1;
function initMap() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var initialLatlng = {lat: position.coords.latitude, lng: position.coords.longitude};

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
        });
    }
}
initMap();