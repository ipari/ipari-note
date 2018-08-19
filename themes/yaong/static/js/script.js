document.addEventListener("DOMContentLoaded", function() {
    // nav 토글 버튼에 이벤트를 붙힌다.
    let menuButton = select("header button");
    menuButton.addEventListener("click", function() {
        toggleNav();
    });

    // nav 에 초기값 지정
    let nav = select("nav");
    nav.style.display = "none";
});

window.addEventListener("load", function() {
    // header 의 햄버거 메뉴 수직 가운데 정렬
    let headerHeight = parseInt(getElementValue("header div.page", "height"));
    let menuButtonHeight = parseInt(getElementValue("header button", "height"));
    let marginTop = (headerHeight - menuButtonHeight) / 2 + "px";
    setElementValue("header button", "marginTop", marginTop);

    setArticleMinHeight();
});

window.addEventListener("resize", function() {
    setArticleMinHeight();
});

function toggleNav() {
    // nav 를 토글한다.
    let nav = select("nav");
    if (nav.style.display === "none") {
        nav.style.display = "block";
    } else {
        nav.style.display = "none";
    }
    setArticleMinHeight();
}

function setArticleMinHeight() {
    // article 의 최소 크기를 footer 가 바닥에 닿을 정도로 설정한다.
    let windowHeight = window.innerHeight;
    let headerHeight = select("header").getBoundingClientRect().height;
    let navHeight = select("nav").getBoundingClientRect().height;

    let article = select("article");
    article.style.height = "auto";
    let articleHeight = select("article").getBoundingClientRect().height;

    let footerHeight = select("footer").getBoundingClientRect().height;
    let minArticleHeight = windowHeight - headerHeight - navHeight - footerHeight;

    if (minArticleHeight > articleHeight) {
        article.style.height = minArticleHeight + "px";
    }
}

function select(query) {
    return document.querySelector(query);
}

function selects(query) {
    return document.querySelectorAll(query);
}


function getElementValue(query, property) {
    let elem = select(query);
    let style = window.getComputedStyle(elem, null);
    return style.getPropertyValue(property);
}


function setElementValue(query, property, value) {
    let elements = selects(query);
    for (let element of elements) {
        element.style[property] = value;
    }
}
