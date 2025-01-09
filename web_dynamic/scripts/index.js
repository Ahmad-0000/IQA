// Here I style the search popover lists
const modifiers = document.getElementById("search-modifiers");
const modifiersPopover = document.getElementById("modifiers-popover");
const modifiersCloser = document.getElementById("modifiers-closer");
const categories = document.getElementById("search-categories");
const categoriesPopover = document.getElementById("categories-popover");
const categoriesCloser = document.getElementById("categories-closer");
const quizzesWrapper = document.querySelector(".quizzes-wrapper")


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


// Fetch categories and give ids

fetch("http://localhost:5001/api/v1/categoreis").then(res => {
    if (res.status == 200) {
        return res.json()
    }
}).then((categoreis) => {
    for (const cat of categoreis) {
        const htmlCat = document.querySelector(`#categories i[title='${cat.name}']`);
        htmlCat.setAttribute('data-id', cat.id);
    }
})


const dateFilter = document.querySelector(".filters div:first-of-type");
const orderTypeDiv = document.querySelector(".filters div:nth-child(2)");
const orderTypeElement = document.querySelector(".filters div:nth-child(2) i");
const popularityFilter = document.querySelector(".filters div:last-of-type");
const filterTrigger = document.querySelector(".filters > i:last-child");
const quizzesCache = [];
let filterCats = [];
let orderType = "desc";
let orderAttribute = "";

dateFilter.addEventListener('click', () => {
    if (dateFilter.hasAttribute("checked")) {
        dateFilter.removeAttribute("checked");
        orderAttribute = ""
    } else {
        if (popularityFilter.hasAttribute("checked")) {
            popularityFilter.removeAttribute("checked")
        }
        dateFilter.setAttribute("checked", true);
        orderAttribute = "added_at";
    }
});

popularityFilter.addEventListener('click', () => {
    if (popularityFilter.hasAttribute("checked")) {
        popularityFilter.removeAttribute("checked");
        orderAttribute = ""
    } else {
        if (dateFilter.hasAttribute("checked")) {
            dateFilter.removeAttribute("checked");
        }
        popularityFilter.setAttribute("checked", true);
        orderAttribute = "times_taken";
    }
});

orderTypeDiv.addEventListener('click', () => {
    if (orderTypeElement.getAttribute("order-type") === "desc") {
        orderTypeElement.setAttribute("order-type", "asc");
        orderType = "asc";
    } else if (orderTypeElement.getAttribute("order-type") === 'asc') {
        orderTypeElement.setAttribute("order-type", "desc");
        orderType = "desc";
    }
});

for (const cat of cats) {
    cat.addEventListener('click', () => {
        if (cat.hasAttribute("checked")) {
            cat.removeAttribute("checked");
            filterCats = filterCats.filter((element) => cat.getAttribute("title") !== element);

        } else {
            cat.setAttribute("checked", "true");
            filterCats.push(cat.getAttribute("title"));
        }
    });
}

filterTrigger.addEventListener('click', () => {
    let url;
    if (! orderAttribute) {
        orderAttribute = "added_at";
    }
    if (! orderType) {
        orderType = "desc";
    }
    if (filterCats.length === 0) {
        url = `http://localhost:5001/api/v1/quizzes?order_attribute=${orderAttribute}&order_type=${orderType}`;
    } else {
        url = `http://localhost:5001/api/v1/quizzes?cats=${filterCats.join(',')}&order_attribute=${orderAttribute}&order_type=${orderType}`;
    }
    fetch(url).then((res) => {
        if (res.ok) {
            return res.json();
            quizzesCache = [];
        } else {
            // Show error page
            console.log(res);
        }
    }).then((quizzes) => {
        for (const quiz of quizzes) {
            quizzesCache.shift(quiz);
	    quizzesWrapper.innerHTML += `<div class="quiz" data-id="${quiz.id}">
                                           <div class="img"></div>
                                           <div class="info">
                                             <h2>${quiz.title}/h2>
                                             <div class="stats">
                                               <i class="fa-regular fa-heart"><span> ${quiz.likes_num} Likes</span></i>
                                               <i class="fa-solid fa-repeat"><span> ${quiz.times_taken} times</span></i>
                                               <i class="fa-regular fa-clock"><span> ${quiz.duration} Minutes</span></i>
                                             </div>               
                                           </div>
                                         </div>`        
        }
    })
});
