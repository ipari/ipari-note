document.addEventListener("DOMContentLoaded", function() {
    // nav 토글 버튼에 이벤트를 붙힌다.
    let menuButton = select("header button");
    menuButton.addEventListener("click", function() {
        toggleNav();
    });

    // nav 에 초기값 지정
    let nav = select("nav");
    nav.style.display = "none";

    // 노트 권한 폼
    let radios = selects("div.permission input[type=radio]");

    for (let radio of radios) {
        radio.addEventListener("change", function() {
            select("div.permission form").submit();
        });
    }
});

window.addEventListener("load", function() {
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

function previewMarkdown(preview, plainText) {
  let ajax = new XMLHttpRequest();
  let parameters = {
    "raw_md": plainText
  };

  ajax.open("POST", "/preview", true);
  ajax.setRequestHeader("Content-type", "application/json");
  ajax.onreadystatechange = function() {
      if (ajax.readyState === 4 && ajax.status === 200) {
          preview.innerHTML = ajax.responseText;
      }
  };
  ajax.send(JSON.stringify(parameters));
}
