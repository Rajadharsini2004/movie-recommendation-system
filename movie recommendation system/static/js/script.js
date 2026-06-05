async function getRecommendation() {
    let title = document.getElementById("movieInput").value;
    if (!title) return;

    let response = await fetch("/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: title })
    });

    let data = await response.json();

    // Movies
    let moviesList = document.getElementById("moviesList");
    moviesList.innerHTML = "";
    data.movies.forEach(item => {
        let card = `<div class="card">
                        <img src="${item.poster}" alt="${item.title}">
                        <p>${item.title}</p>
                    </div>`;
        moviesList.innerHTML += card;
    });

    // TV Shows
    let tvList = document.getElementById("tvShowsList");
    tvList.innerHTML = "";
    data.tv_shows.forEach(item => {
        let card = `<div class="card">
                        <img src="${item.poster}" alt="${item.title}">
                        <p>${item.title}</p>
                    </div>`;
        tvList.innerHTML += card;
    });
}

