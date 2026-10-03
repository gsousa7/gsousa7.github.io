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

        // Swap only the file name so the site's baseurl prefix (set by
        // Jekyll in the <head> script) is kept.
        var favicon = document.getElementById('theme-favicon');
        if (favicon) {
            favicon.href = favicon.href.replace(/favicon-(dark|light)\.svg/, 'favicon-' + next + '.svg');
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

    // Real in-page anchors, so the TOC works with the keyboard and
    // Ctrl/middle-click; smooth scrolling comes from CSS (and is skipped
    // under prefers-reduced-motion).
    headers.forEach((h) => {
        const sectionId = h.parentElement.id;

        let tocItem = document.createElement("li");
        tocItem.id = "toc-id-" + sectionId;

        let itemLink = document.createElement("a");
        itemLink.classList.add("content-link");
        itemLink.href = "#" + sectionId;
        itemLink.textContent = h.textContent.trim();

        tocItem.append(itemLink);
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
            let tocLink = document.getElementById("toc-id-" + currHead.parentElement.id);
            tocLink.classList.add('active');
            // Mirrors the nav highlight onto the section's own badge, so
            // both agree on which section is "current" instead of only
            // the sidebar knowing.
            currHead.classList.add('active');
        }
    }

    // Recompute only when the page actually scrolls or changes size (window
    // resize, or a "Show details" entry expanding), at most once per frame,
    // instead of polling on a timer forever.
    var scrollStatePending = false;

    function scheduleScrollState(){
        if (scrollStatePending) return;
        scrollStatePending = true;
        requestAnimationFrame(function(){
            scrollStatePending = false;
            updateScrollState();
        });
    }

    updateScrollState();
    window.addEventListener('scroll', scheduleScrollState, { passive: true });
    new ResizeObserver(scheduleScrollState).observe(document.body);

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