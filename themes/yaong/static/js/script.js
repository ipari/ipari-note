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

    // 비디오 폭 설정
    resizeVideos();

    let toTop = select("div.to-top a");
    toTop.addEventListener("click", function(e) {
       window.scrollTo(0, 0);
       e.preventDefault();
    });

    // 테이블 헤더 정렬 기능
    // https://stackoverflow.com/questions/14267781/sorting-html-table-with-javascript
    const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

    const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
        v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
        )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

    document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
        const tbody = th.closest('table').querySelector('tbody');
        Array.from(tbody.querySelectorAll('tr:nth-child(n)'))
            .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
            .forEach(tr => tbody.appendChild(tr) );
    })));
});

window.addEventListener("resize", function() {
    resizeVideos();
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

function resizeIFrame() {
    let iframes = selects("iframe");
    iframes.forEach(iframe => {
        iframe.style.display = "block";
        iframe.width = iframe.contentWindow.outerWidth;
        iframe.height = iframe.contentWindow.document.body.scrollHeight;
    });
}

function resizeVideos() {
    let iframes = selects("figure.video iframe");
    iframes.forEach(iframe => {
        iframe.style.display = "block";
        let parentWidth = iframe.parentElement.clientWidth;
        let ratio = parentWidth / iframe.width;
        iframe.width = parentWidth;
        iframe.height = iframe.height * ratio;
    });
}
