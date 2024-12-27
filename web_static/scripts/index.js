// Here I style the search popover lists
const modifiers = document.getElementById("search-modifiers");
const modifiersPopover = document.getElementById("modifiers-popover");
const modifiersCloser = document.getElementById("modifiers-closer");
const categories = document.getElementById("search-categories");
const categoriesPopover = document.getElementById("categories-popover");
const categoriesCloser = document.getElementById("categories-closer");

modifiers.addEventListener('click', () => {
    if (categoriesPopover.style.display === "block") {
        categoriesPopover.style.display = "none";
        categoriesPopover.style.top = "100px";
        categoriesPopover.style.opacity = "0";
    }
    modifiersPopover.style.display = "block";
    setTimeout(() => {
        modifiersPopover.style.opacity = 1;
        modifiersPopover.style.top = "55px"
    }, 0);
});

categories.addEventListener('click', () => {
    if (modifiersPopover.style.display === "block") {
        modifiersPopover.style.display = "none";
        modifiersPopover.style.top = "100px";
        modifiersPopover.style.opacity = "0";
    }
    categoriesPopover.style.display = "block";
    setTimeout(() => {
        categoriesPopover.style.opacity = "1";
        categoriesPopover.style.top = "55px";
    }, 0);
});

modifiersCloser.addEventListener('click', () => {
    modifiersPopover.style.opacity = "0";
    modifiersPopover.style.top = "100px";
    setTimeout(() => {
        modifiersPopover.style.display = "none";
    }, 300);
});

categoriesCloser.addEventListener('click', () => {
    categoriesPopover.style.opacity = "0";
    categoriesPopover.style.top = "100px";
    setTimeout(() => {
        categoriesPopover.style.display = "none";
    }, 300);
});

// Categories Icons container and children
const catsHolder = document.querySelector("#categories");
const cats = Array.from(catsHolder.children);

// Stop the animation when hovering over an icon, resume otherwise
cats.forEach((hoveredCat) => {
    hoveredCat.addEventListener('mouseenter', () => {
        cats.forEach((cat) => {
            cat.style.animationPlayState = "paused";
        }); 
    });

    hoveredCat.addEventListener('mouseleave', () => {
        cats.forEach((cat) => {
            cat.style.animationPlayState = "running";
        });
    });
});

// Handle overlay and quiz card details when clicking over a quiz card
const page = document.querySelector(".page");
const overlayLayer = document.getElementById("quiz-overlay");
const quizBoxes = document.getElementsByClassName("quiz");
const quizDetails = document.getElementById("quiz-details");
const quizDetailsCloser = document.getElementById('quiz-details-closer');

const originalQuizDetailsClasses = quizDetails.className;
const originalOverlayClasses = overlayLayer.className;

for (const quizBox of quizBoxes) {
    quizBox.addEventListener('click', () => {
        overlayLayer.style.display = "block";

        setTimeout(() => {
            overlayLayer.style.filter = "blur(4px)";
        }, 20);
    });

    quizBox.addEventListener('click', () => {
        quizDetails.style.display = "flex";
        setTimeout(() => {
            quizDetails.style.transform = "translate(-50%, -50%)";
            quizDetails.style.opacity = "1";
        }, 0);
    });
}

quizDetailsCloser.addEventListener('click', () => {
    overlayLayer.style.display = "none";
    quizDetails.style.transform = "translate(-50%, 0)";
    quizDetails.style.opacity = "0";
    setTimeout(() => {
        quizDetails.style.display = "none";
    }, 500);
});