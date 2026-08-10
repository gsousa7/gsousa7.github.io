document.addEventListener('DOMContentLoaded', function(){
    const themeToggle = document.getElementById('theme-toggle');

    themeToggle.addEventListener('click', function(){
        var current = document.documentElement.getAttribute('data-theme');

        if (!current) {
            current = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }

        var next = current === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);

        var favicon = document.getElementById('theme-favicon');
        if (favicon) {
            favicon.href = next === 'dark'
                ? '/assets/img/favicon-dark.svg'
                : '/assets/img/favicon-light.svg';
        }
    });

    document.querySelectorAll('img[alt="devicon"][title]').forEach((icon) => {
        const wrap = document.createElement('span');
        wrap.className = 'devicon-tip';
        wrap.dataset.tip = icon.title;
        icon.removeAttribute('title');
        icon.replaceWith(wrap);
        wrap.append(icon);
    });

    const tocbox = document.querySelector('.toc-box');
    var headers = document.querySelectorAll('.subject-name');

    headers.forEach((h) => {
        let tocItem = document.createElement("li");
        tocItem.id = "toc-id-" + h.textContent;

        let itemLink = document.createElement("a");
        itemLink.classList.add("content-link");
        itemLink.textContent = h.textContent;

        tocItem.append(itemLink);

        tocItem.addEventListener('click', function(){
            h.scrollIntoView({
                behavior: 'smooth'
            });
        });

        tocbox.append(tocItem);
    });

    function updateScrollState(){
        var scrollPos = document.documentElement.scrollTop;
        var wh = window.innerHeight;
        var maxScroll = document.documentElement.scrollHeight - wh;

        Array.from(tocbox.querySelectorAll('li')).forEach(function(tocItem){
            tocItem.classList.remove('active');
        });

        Array.from(headers).forEach(function(h){
            h.classList.remove('active');
        });

        var currHead;

        Array.from(headers).forEach(function(h){
            let headPos = h.getBoundingClientRect().top + window.scrollY - wh/2;

            if (scrollPos > headPos) currHead = h;
        });

        // The midpoint check above can leave the very first or very last
        // section unreachable (a short section's own threshold can fall
        // before the page even loads, or past the page's actual max
        // scroll) — pin them explicitly at the scroll extremes instead.
        if (scrollPos <= 0) {
            currHead = headers[0];
        } else if (scrollPos >= maxScroll - 1) {
            currHead = headers[headers.length - 1];
        }

        if (currHead != undefined){
            let tocLink = document.getElementById("toc-id-" + currHead.textContent);
            tocLink.classList.add('active');
            // Mirrors the nav highlight onto the section's own badge, so
            // both agree on which section is "current" instead of only
            // the sidebar knowing.
            currHead.classList.add('active');
        }
    }

    updateScrollState();
    setInterval(updateScrollState, 200);

    // A closed <details> renders no content at all when printed (Chromium's
    // internal ::details-content wrapper can't be overridden by author CSS)
    // — force every collapsible entry open for the duration of the print,
    // then restore whatever state each one was actually in.
    var collapsedBeforePrint = [];

    window.addEventListener('beforeprint', function(){
        collapsedBeforePrint = Array.from(document.querySelectorAll('.collapsible-entry:not([open])'));
        collapsedBeforePrint.forEach((el) => { el.open = true; });
    });

    window.addEventListener('afterprint', function(){
        collapsedBeforePrint.forEach((el) => { el.open = false; });
        collapsedBeforePrint = [];
    });
});