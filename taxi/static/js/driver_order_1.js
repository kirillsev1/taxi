function initMap() {
    {% if order.order %}
        const arrPointString = "{{ order.order.arrival }}";
        const depPointString = "{{ order.order.departure }}";
    {% else %}
        const arrPointString = "{{ order.arrival }}";
        const depPointString = "{{ order.departure }}";
    {% endif %}
    const depPointArray = depPointString.match(/POINT \(([0-9.-]+) ([0-9.-]+)\)/);
    const depLat = parseFloat(depPointArray[2]);
    const depLng = parseFloat(depPointArray[1]);


    const arrPointArray = arrPointString.match(/POINT \(([0-9.-]+) ([0-9.-]+)\)/);
    const arrLat = parseFloat(arrPointArray[2]);
    const arrLng = parseFloat(arrPointArray[1]);
    const coordinatesDiv = document.getElementById("coordinates");

    coordinatesDiv.innerHTML = "Latitude: " + depLat + ", Longitude: " + depLng;

    const map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: depLat, lng: depLng },
        zoom: 16,
    });

    new google.maps.Marker({
        position: { lat: depLat, lng: depLng },
        map,
        title: "Departure",
        icon: {
            url: 'http://maps.google.com/mapfiles/ms/icons/pink-dot.png'
        }
    });

    new google.maps.Marker({
        position: { lat: arrLat, lng: arrLng },
        map,
        title: "Arrival",
    });

    const flightPlanCoordinates = [
        { lat: depLat, lng: depLng },
        { lat: arrLat, lng: arrLng }
        ]
    const trafficLayer = new google.maps.TrafficLayer();
    trafficLayer.setMap(map);
    const flightPath = new google.maps.Polyline({
        path: flightPlanCoordinates,
        geodesic: true,
        strokeColor: "#FF0000",
        strokeOpacity: 1.0,
        strokeWeight: 2,
    });

  flightPath.setMap(map)
}