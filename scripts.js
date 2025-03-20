function load_recent_songs(){
  fetch("./recent_tracks.json")
    .then(response => response.json())
    .then(data => {
      const recentTracksList = document.getElementById("recent-tracks");
      recentTracksList.innerHTML = ''; // Clear previous tracks

      data.forEach(track => {
        const trackElement = document.createElement("div");
        trackElement.innerHTML = `
        <div class="track-item">
            <img src="${track.album_image}" alt="${track.name} by ${track.artists}" height="128px" width="128px">
            <div>
                <h3 href=${track.link}>${track.name}</h3>
                <p>${track.artists}</p>
            </div>
          </div>
        `;
        recentTracksList.appendChild(trackElement);
    });
  })
  .catch(error => {
      console.error("Error loading recent tracks:", error);
  });
}

