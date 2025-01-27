// Start a quiz when clicking "start" button
const startButton = document.getElementById("start");
const introduction = document.getElementById("introduction");
const questionTemplate = document.getElementById("question-template");

startButton.addEventListener('click', () => {
    introduction.style.display = "none";
    questionTemplate.style.display = "block";
});