// Here I style the navigation bar on the mobile
const navBar = document.getElementById("navigation-bar");
const burgerIcon = document.getElementById("burger-icon");

// Handle the Burger Icon "click" event on small screens
burgerIcon.addEventListener('click', () => {
  if (navBar.style.width === "" ) {
    navBar.style.width = "50%";
    burgerIcon.children[1].style.width = "100%";

  } else {
    navBar.style.width = "";
    burgerIcon.children[1].style.width = "50%";
  }
});
