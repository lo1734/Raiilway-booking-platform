document.getElementById("searchForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let source = document.getElementById("source").value;
    let destination = document.getElementById("destination").value;
    let travelDate = document.getElementById("travelDate").value;

    fetch(`/search/?source=${source}&destination=${destination}&date=${travelDate}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById("searchResults").innerHTML = `<p style="color:red;">${data.error}</p>`;
            } else {
                let results = data.trains.map(train =>
                    `<p><strong>${train.train_number} - ${train.train_name}</strong> (Seats Left: ${train.seats_left})</p>`
                ).join("");
                document.getElementById("searchResults").innerHTML = results || "<p>No trains available on this day.</p>";
            }
        })
        .catch(error => console.error("Error:", error));
});


//document.getElementById("searchForm").addEventListener("submit", function(event) {
//    event.preventDefault();
//    let source = document.getElementById("source").value;
//    let destination = document.getElementById("destination").value;
//
//    fetch(`/search/?source=${source}&destination=${destination}`)
//    .then(response => response.json())
//    .then(data => {
//        let results = data.trains.map(train =>
//            `<p>${train.train_number} - ${train.train_name} (Seats Left: ${train.seats_left})</p>`
//        ).join("");
//        document.getElementById("searchResults").innerHTML = results;
//    });
//});
