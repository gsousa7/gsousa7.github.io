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

        Array.from(tocbox.querySelectorAll('li')).forEach(function(tocItem){
            tocItem.classList.remove('active');
        });

        var currHead;

        Array.from(headers).forEach(function(h){
            let headPos = h.getBoundingClientRect().top + window.scrollY - wh/2;

            if (scrollPos > headPos) currHead = h;
        });

        if (currHead != undefined){
            let tocLink = document.getElementById("toc-id-" + currHead.textContent);
            tocLink.classList.add('active');
        }
    }

    updateScrollState();
    setInterval(updateScrollState, 200);
});