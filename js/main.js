// Shared behavior for every page: mobile nav toggle, solid nav on scroll,
// and the fullscreen photo lightbox (arrows, swipe, keyboard, close).

document.addEventListener("DOMContentLoaded", function () {
  // --- Mobile nav toggle ---
  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    var closeMenu = function () {
      links.classList.remove("open");
      toggle.innerHTML = "&#9776;";
      document.body.style.overflow = "";
    };
    toggle.addEventListener("click", function () {
      var isOpen = links.classList.toggle("open");
      toggle.innerHTML = isOpen ? "&times;" : "&#9776;";
      document.body.style.overflow = isOpen ? "hidden" : "";
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", closeMenu);
    });
    links.addEventListener("click", function (e) {
      if (e.target === links) closeMenu();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && links.classList.contains("open")) closeMenu();
    });
  }

  // --- Solid nav background once you scroll past the hero ---
  var nav = document.querySelector(".site-nav");
  if (nav && !nav.classList.contains("always-solid")) {
    window.addEventListener("scroll", function () {
      if (window.scrollY > 40) {
        nav.classList.add("solid");
      } else {
        nav.classList.remove("solid");
      }
    });
  }

  // --- Lightbox ---
  var triggers = Array.prototype.slice.call(document.querySelectorAll("[data-lightbox-full]"));
  if (!triggers.length) return;

  var lightbox = document.createElement("div");
  lightbox.className = "lightbox";
  lightbox.innerHTML =
    '<button class="lightbox-close" aria-label="Close">&times;</button>' +
    '<button class="lightbox-prev" aria-label="Previous">&#10094;</button>' +
    '<img alt="">' +
    '<button class="lightbox-next" aria-label="Next">&#10095;</button>' +
    '<div class="lightbox-counter"></div>';
  document.body.appendChild(lightbox);

  var imgEl = lightbox.querySelector("img");
  var counterEl = lightbox.querySelector(".lightbox-counter");
  var current = 0;

  function show(index) {
    current = (index + triggers.length) % triggers.length;
    var t = triggers[current];
    var nextSrc = t.getAttribute("data-lightbox-full");
    if (imgEl.src === nextSrc) return;
    imgEl.classList.add("switching");
    window.setTimeout(function () {
      imgEl.src = nextSrc;
      imgEl.alt = t.getAttribute("data-lightbox-alt") || "";
      counterEl.textContent = (current + 1) + " / " + triggers.length;
      imgEl.classList.remove("switching");
    }, 150);
  }

  function open(index) {
    show(index);
    lightbox.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function close() {
    lightbox.classList.remove("open");
    document.body.style.overflow = "";
  }

  triggers.forEach(function (t, i) {
    t.addEventListener("click", function () { open(i); });
  });

  lightbox.querySelector(".lightbox-close").addEventListener("click", close);
  lightbox.querySelector(".lightbox-prev").addEventListener("click", function () { show(current - 1); });
  lightbox.querySelector(".lightbox-next").addEventListener("click", function () { show(current + 1); });
  lightbox.addEventListener("click", function (e) {
    if (e.target === lightbox) close();
  });

  document.addEventListener("keydown", function (e) {
    if (!lightbox.classList.contains("open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(current - 1);
    if (e.key === "ArrowRight") show(current + 1);
  });

  // Swipe support for touch devices
  var touchStartX = null;
  lightbox.addEventListener("touchstart", function (e) {
    touchStartX = e.changedTouches[0].clientX;
  }, { passive: true });
  lightbox.addEventListener("touchend", function (e) {
    if (touchStartX === null) return;
    var dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) > 40) {
      if (dx < 0) show(current + 1);
      else show(current - 1);
    }
    touchStartX = null;
  }, { passive: true });
});
