function latLngPop(e) {
            var coords = {
                lat: e.latlng.lat,
                lng: e.latlng.lng,
                timestamp: Date.now()
            };

            var popupName = Object.keys(window).find(key => key.includes('lat_lng_popup_'));
            var mapName = Object.keys(window).find(key => key.includes('map_'));

            if (popupName && mapName) {
                window[popupName]
                    .setLatLng(e.latlng)
                    .setContent(
                        "<div style='font-family: Segoe UI; color: white; font-size: 12px;'>" +
                        "<button id='addLocationBtn' class='custom-popup-btn'>➕ Dodaj lokalizację</button>" +
                        "<br><br>Lat: " + e.latlng.lat.toFixed(6) +
                        "<br>Lng: " + e.latlng.lng.toFixed(6) +
                        "<br>Czas: " + new Date().toLocaleString() +
                        "</div>"
                    )

                    .openOn(window[mapName]);

                setTimeout(function() {
                    var btn = document.getElementById('addLocationBtn');
                    if (btn) {
                        btn.addEventListener('click', function() {
                            localStorage.setItem('lastCoordinates', JSON.stringify(coords));
                        });
                    }
                }, 0);
            }
        }