
function go(url) {
    sessionStorage.setItem("nextPage", url);
    window.location.href = "/loading";
}

