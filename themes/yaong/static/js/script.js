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

function toggleNav() {
    // nav 를 토글한다.
    let nav = select("nav");
    if (nav.style.display === "none") {
        nav.style.display = "block";
    } else {
        nav.style.display = "none";
    }
}

function select(query) {
    return document.querySelector(query);
}

function selects(query) {
    return document.querySelectorAll(query);
}

function previewMarkdown(preview, plainText, url) {
  let ajax = new XMLHttpRequest();
  let parameters = {
    "raw_md": plainText
  };

  ajax.open("POST", url, true);
  ajax.setRequestHeader("Content-type", "application/json");
  ajax.onreadystatechange = function() {
      if (ajax.readyState === 4 && ajax.status === 200) {
          preview.innerHTML = ajax.responseText;
      }
  };
  ajax.send(JSON.stringify(parameters));
}
