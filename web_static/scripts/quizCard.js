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