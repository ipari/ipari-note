document.addEventListener("DOMContentLoaded", function() {
    let menuButton =
        document.querySelector("header button")
    menuButton.addEventListener("click", function(e) {
        toggleNav();
    });

    let nav = document.querySelector("nav");
    nav.style.display = "none";
});


function toggleNav() {
    let nav = document.querySelector("nav");
    if (nav.style.display === "none") {
        nav.style.display = "block";
    } else {
        nav.style.display = "none";
    }
}
