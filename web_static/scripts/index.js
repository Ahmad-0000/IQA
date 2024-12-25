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