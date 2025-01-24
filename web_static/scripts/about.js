const h3s = document.querySelectorAll("h3");

h3s.forEach((h3) => {
    h3.addEventListener('click', () => {
        const itsParagraph = h3.nextElementSibling;
        const itsArrow = h3.children[0];
        if (itsParagraph.style.height === "0px"  || itsParagraph.style.height === "") {
            h3.style.color = "#0075ff";
            itsParagraph.style.height = itsParagraph.scrollHeight + 20 + 'px';
            itsParagraph.style.paddingTop = "10px";
            itsArrow.style.transform = "rotate(90deg)";
            itsArrow.style.color = "#0075ff";
        } else {
            h3.style.color = "#888";
            itsParagraph.style.height = "0px";
            itsParagraph.style.paddingTop = "0px"
            itsArrow.style.transform = "rotate(0deg)";
            itsArrow.style.color = "#888";
        }
    });
});
