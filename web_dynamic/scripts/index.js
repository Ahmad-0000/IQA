// Here I style the search popover lists
const modifiers = document.getElementById("search-modifiers");
const modifiersPopover = document.getElementById("modifiers-popover");
const modifiersCloser = document.getElementById("modifiers-closer");
const categories = document.getElementById("search-categories");
const categoriesPopover = document.getElementById("categories-popover");
const categoriesCloser = document.getElementById("categories-closer");
const quizzesWrapper = document.querySelector(".quizzes-wrapper")

// Handle error response
const errorPage = document.querySelector("#error");
const errorCode = document.querySelector("#error h1 span");
const errorMessage = document.querySelector("#error p:first-of-type");

async function showErrorPage(res) {
    // Show the error page
    errorPage.style.display = "flex";
    const data = await res.json();
    errorCode.textContent = res.status;
    errorMessage.textContent = data.error;
  }

// Hide error page
errorPage.children[0].addEventListener('click', () => {
    errorPage.style.display = "none";
})

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

// Fetch filtered quizzes
let attribute = "added_at"; 
let after = "initial";
let type = "desc"; // Ordering type
let searchCategories = [];
let url = "http://localhost:5001/api/v1/quizzes?attribute=added_at&type=desc&after=initial";
let quizzesCache = [];
let fresh = false;

async function getQuizzes () {
    fetch(url).then((res) => {
        if (res.ok) {
            return res.json();
        } else {
            showErrorPage(res);
            throw new Error();
        }
    }).then((quizzes) => {
        if (fresh) {
           quizzesWrapper.innerHTML = "";
        }
        for (const quiz of quizzes) {
            quizzesWrapper.innerHTML += `<div class="quiz" data-id="${quiz.id}">
                                            <div class="img"></div>
                                            <div class="info">
                                                    <h2>${quiz.title}</h2>
                                                    <div class="stats">
                                                    <i class="fa-regular fa-heart"><span> ${quiz.likes_num} Likes</span></i>
                                                    <i class="fa-solid fa-repeat"><span> ${quiz.repeats} times</span></i>
                                                    <i class="fa-regular fa-clock"><span> ${quiz.duration} Minutes</span></i>
                                            </div>
                                            </div>
                                        </div>`;
        };
    }, (error) => {});
}

qetQuizzes();
// implement like and remove-like functionality
// document.addEventListener("click", function (event) {
//   if (event.target.classList.contains("like-icon")) {
//   if (event.target.classList.contains("liked")) {} else {
//   fetch("http://localhost:5001/api/v1/remove_like?quiz_id=${event.target.parentElement.parentElement.dataId}"), {method: "DELETE", credentials: "include"}).then(res => {
//   if (res.ok) {
//     // reduce the likes number + change color
// } else {
//     showErrorPage(res);
// }
// })
// }
// });