// Here I style the search popover lists
const modifiers = document.getElementById("search-modifiers");
const modifiersPopover = document.getElementById("modifiers-popover");
const modifiersCloser = document.getElementById("modifiers-closer");
const categories = document.getElementById("search-categories");
const categoriesPopover = document.getElementById("categories-popover");
const categoriesCloser = document.getElementById("categories-closer");
const quizzesWrapper = document.querySelector(".quizzes-wrapper")

async function showErrorPage(response) {
  // Show the error page
  errorPage.style.display = "flex";
  const data = await response.json();
  errorCode.textContent = data.status;
  errorMessage.textContent = data.body;
}

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
const page = document.querySelector(".page");
const overlayLayer = document.getElementById("quiz-overlay");
const quizDetails = document.getElementById("quiz-details");
const quizDetailsCloser = document.getElementById('quiz-details-closer');
const quizTitle = document.getElementById("title");
const quizDescription = document.getElementById("description");
const quizUser = document.getElementById("user");
const quizAddTime = document.getElementById("added_at");
const quizUpdateTime = document.getElementById("updated_at");
const quizDifficulty = document.getElementById("difficulty");
const quizLikes = document.getElementById("likes");
const quizRepeats = document.getElementById("times_taken");
const quizDuration = document.getElementById("duration");
const originalQuizDetailsClasses = quizDetails.className;
const originalOverlayClasses = overlayLayer.className;
let quizBoxes;
const dateFilter = document.querySelector(".filters div:first-of-type");
const orderTypeDiv = document.querySelector(".filters div:nth-child(2)");
const orderTypeElement = document.querySelector(".filters div:nth-child(2) i");
const popularityFilter = document.querySelector(".filters div:last-of-type");
const filterTrigger = document.querySelector(".filters > i:last-child");
const more = document.querySelector("#more");
let url;
let quizzesCache = [];
let filterCats = [];
let orderType = "desc";
let after = "initial";
let orderAttribute = "added_at";


fetch(`http://localhost:5001/api/v1/quizzes?order_attribute=${orderAttribute}&order_type=${orderType}&after=${after}`).then((res) => {
        if (res.ok) {
            return res.json();
        } else {
           showErrorPage(res); 
        }
    }).then((quizzes) => {
        quizzesCache = [];
	if (quizzes.length === 0) {
		quizzesWrapper.innerHTML = `<p id="empty-result">No results<p>`;
	}
        for (const quiz of quizzes) {
            quizzesCache.unshift(quiz);
	        quizzesWrapper.innerHTML += `<div class="quiz" data-id="${quiz.id}">
                                            <div class="img"></div>
                                            <div class="info">
                                                    <h2>${quiz.title}</h2>
                                                    <div class="stats">
                                                    <i class="fa-regular fa-heart"><span> ${quiz.likes_num} Likes</span></i>
                                                    <i class="fa-solid fa-repeat"><span> ${quiz.times_taken} times</span></i>
                                                    <i class="fa-regular fa-clock"><span> ${quiz.duration} Minutes</span></i>
                                                    </div>
                                            </div>
                                        </div>`
        }
        if (quizzesCache[quizzesCache.length - 1]) {
            after = quizzesCache[quizzesCache.length - 1].getAttribute(orderAttribute);
        }
	
	// Handle overlay and quiz card details when clicking over a quiz card
	quizBoxes = document.getElementsByClassName("quiz");
	for (const quizBox of quizBoxes) {
	    quizBox.addEventListener('click', () => {
	        overlayLayer.style.display = "block";
	        setTimeout(() => {
        	    overlayLayer.style.filter = "blur(4px)";
	        }, 20);
	    });

	    quizBox.addEventListener('click', () => {
		const [me] = quizzesCache.filter((quiz) => quiz.id === quizBox.getAttribute("data-id"));
		quizTitle.textContent = me.title;
		quizDescription.textContent = me.description;
		quizUser.textContent = me.user_id;
		quizAddTime.textContent = me.added_at.split('T')[0] + ' ' + me.added_at.split('T')[1] + ' UTC';
		quizUpdateTime.textContent = me.updated_at.split('T')[0] + ' ' + me.updated_at.split('T')[1] + ' UTC';
		if (me.added_at = me.updated_at) {
                    quizUpdateTime.textContent = 'None';
		}
		quizDifficulty.textContent = me.difficulty;
		quizLikes.textContent += me.likes_num;
		quizRepeats.textContent += me.times_taken;
		quizDuration.textContent += me.duration + ' Minutes';
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
    });


dateFilter.addEventListener('click', () => {
    if (dateFilter.hasAttribute("checked")) {
        dateFilter.removeAttribute("checked");
        orderAttribute = "";
	after = "initial";
    } else {
        if (popularityFilter.hasAttribute("checked")) {
            popularityFilter.removeAttribute("checked")
        }
        dateFilter.setAttribute("checked", true);
        orderAttribute = "added_at";
	if (quizzesCache[quizzesCache.length - 1]) {
	  after = quizzesCache[quizzesCache.length - 1].added_at;
	}
    }
});

popularityFilter.addEventListener('click', () => {
    if (popularityFilter.hasAttribute("checked")) {
        popularityFilter.removeAttribute("checked");
        orderAttribute = ""
	after = "initial";
    } else {
        if (dateFilter.hasAttribute("checked")) {
            dateFilter.removeAttribute("checked");
        }
        popularityFilter.setAttribute("checked", true);
        orderAttribute = "times_taken";
	if (quizzesCache[quizzesCache.length - 1]) {
	  after = quizzesCache[quizzesCache.length - 1].times_taken;
	}
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
    if (! orderAttribute) {
        orderAttribute = "added_at";
    }
    if (! orderType) {
        orderType = "desc";
    }
    if (filterCats.length === 0) {
        url = `http://localhost:5001/api/v1/quizzes?order_attribute=${orderAttribute}&order_type=${orderType}&after=${after}`;
    } else {
        url = `http://localhost:5001/api/v1/quizzes?cats=${filterCats.join(',')}&order_attribute=${orderAttribute}&order_type=${orderType}&after=${after}`;
    }
    fetch(url).then((res) => {
        if (res.ok) {
            return res.json();
        } else {
           showErrorPage(res); 
        }
    }).then((quizzes) => {
        quizzesWrapper.innerHTML = "";
        quizzesCache = [];
        console.log(quizzes);
        if (quizzes.length === 0) {
            alert("No more results");
            return;
        }
        for (const quiz of quizzes) {
            quizzesCache.unshift(quiz);
	        quizzesWrapper.innerHTML += `<div class="quiz" data-id="${quiz.id}">
                                            <div class="img"></div>
                                            <div class="info">
                                                <h2>${quiz.title}</h2>
                                                <div class="stats">
                                                    <i class="fa-regular fa-heart"><span> ${quiz.likes_num} Likes</span></i>
                                                    <i class="fa-solid fa-repeat"><span> ${quiz.times_taken} times</span></i>
                                                    <i class="fa-regular fa-clock"><span> ${quiz.duration} Minutes</span></i>
                                                </div>
                                            </div>
                                        </div>`
        }
        if (quizzesCache[quizzesCache.length - 1]) {
            after = quizzesCache[quizzesCache.length - 1].getAttribute(orderAttribute);
        }
	
	// Handle overlay and quiz card details when clicking over a quiz card
	quizBoxes = document.getElementsByClassName("quiz");
	for (const quizBox of quizBoxes) {
	    quizBox.addEventListener('click', () => {
	        overlayLayer.style.display = "block";
	        setTimeout(() => {
        	    overlayLayer.style.filter = "blur(4px)";
	        }, 20);
	    });

	    quizBox.addEventListener('click', () => {
		const [me] = quizzesCache.filter((quiz) => quiz.id === quizBox.getAttribute("data-id"));
		quizTitle.textContent = me.title;
		quizDescription.textContent = me.description;
		quizUser.textContent = me.user_id;
		quizAddTime.textContent = me.added_at.split('T')[0] + ' ' + me.added_at.split('T')[1] + ' UTC';
		quizUpdateTime.textContent = me.updated_at.split('T')[0] + ' ' + me.updated_at.split('T')[1] + ' UTC';
		if (me.added_at = me.updated_at) {
                    quizUpdateTime.textContent = 'None';
		}
		quizDifficulty.textContent = me.difficulty;
		quizLikes.textContent += me.likes_num;
		quizRepeats.textContent += me.times_taken;
		quizDuration.textContent += me.duration + ' Minutes';
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
    });
});

more.addEventListener('click', () => {
    if (filterCats.length > 0) {
        url = `http://localhost:5001/api/v1/quizzes?cats=${filterCats.join(',')}&order_attribute=${orderAttribute}&order_type=${orderType}`;
    } else {
        url = `http://localhost:5001/api/v1/quizzes?order_attribute=${orderAttribute}&order_type=${orderType}`;
    }
    fetch(url).then((res) => {
        if (res.ok) {
            return res.json();
        } else {
            showErrorPage(res);
        }
    }).then((quizzes) => {
        if (quizzes.length === 0) {
            alert("No more results");
            return;
        }
        for (const quiz of quizzes) {
            quizzesCache.unshift(quiz);
	        quizzesWrapper.innerHTML += `<div class="quiz" data-id="${quiz.id}">
                                            <div class="img"></div>
                                            <div class="info">
                                                <h2>${quiz.title}</h2>
                                                <div class="stats">
                                                    <i class="fa-regular fa-heart"><span> ${quiz.likes_num} Likes</span></i>
                                                    <i class="fa-solid fa-repeat"><span> ${quiz.times_taken} times</span></i>
                                                    <i class="fa-regular fa-clock"><span> ${quiz.duration} Minutes</span></i>
                                                </div>
                                            </div>
                                        </div>`
        }
        if (quizzesCache[quizzesCache.length - 1]) {
            after = quizzesCache[quizzesCache.length - 1].getAttribute(orderAttribute);
        }
	
	// Handle overlay and quiz card details when clicking over a quiz card
	quizBoxes = document.getElementsByClassName("quiz");
	for (const quizBox of quizBoxes) {
	    quizBox.addEventListener('click', () => {
	        overlayLayer.style.display = "block";
	        setTimeout(() => {
        	    overlayLayer.style.filter = "blur(4px)";
	        }, 20);
	    });

	    quizBox.addEventListener('click', () => {
		const [me] = quizzesCache.filter((quiz) => quiz.id === quizBox.getAttribute("data-id"));
		quizTitle.textContent = me.title;
		quizDescription.textContent = me.description;
		quizUser.textContent = me.user_id;
		quizAddTime.textContent = me.added_at.split('T')[0] + ' ' + me.added_at.split('T')[1] + ' UTC';
		quizUpdateTime.textContent = me.updated_at.split('T')[0] + ' ' + me.updated_at.split('T')[1] + ' UTC';
		if (me.added_at = me.updated_at) {
                    quizUpdateTime.textContent = 'None';
		}
		quizDifficulty.textContent = me.difficulty;
		quizLikes.textContent += me.likes_num;
		quizRepeats.textContent += me.times_taken;
		quizDuration.textContent += me.duration + ' Minutes';
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
  })
});
