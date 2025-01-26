const questionContainer = document.querySelector("#questionsContainer");
const newQuestion = document.querySelector("#new-question");
const deleteQuestion = document.querySelector("#delete-question");
let newAnswer = document.getElementsByClassName("newAnswer");
let deleteAnswer = document.getElementsByClassName("deleteAnswer");
const myForm = document.querySelector("form");
const errorPage = document.querySelector("#error");
const errorCode = document.querySelector("#error div h1 span ")
const errorMessage = document.querySelector("#error p:first-of-type");
let questionsNum = 1

// Handle error response
async function showErrorPage(res) {
    // Show the error page
    errorPage.style.display = "flex";
    const data = await res.json();
    errorCode.textContent = res.status;
    errorMessage.textContent = data.error;
}

addNewAnswerEventHandler(newAnswer[0]);
addDeleteAnswerEventHandler(deleteAnswer[0]);

newQuestion.addEventListener('click', () => {
    questionsNum += 1
    questionContainer.innerHTML += `<div class="question-${questionsNum} border p-10 rad-10">
                                        <label>
                                            Body:
                                            <input type="text" max="265" required>
                                        </label>
                                        <p>Answers: <i class="fa-solid fa-plus newAnswer"></i> <i class="fa-solid fa-minus deleteAnswer"></i></p>
                                        <label class="answer-${questionsNum}">
                                            <div class="answer"><input type="radio" name="answer-${questionsNum}" required> <input type="text" required></div>
                                            <div class="answer"><input type="radio" name="answer-${questionsNum}" required> <input type="text" required></div>
                                        </label>
                                    </div>`
    newAnswer = document.getElementsByClassName("newAnswer");
    deleteAnswer = document.getElementsByClassName("deleteAnswer");
    for (const answer of newAnswer) {
        addNewAnswerEventHandler(answer);
    }
    for (const answer of deleteAnswer) {
        addDeleteAnswerEventHandler(answer);
    }
})

deleteQuestion.addEventListener('click', () => {
    if (questionsNum === 1) {
        alert("At least one question is required");
    } else {
        const targetElement = document.querySelector(`#questionsContainer .question-${questionsNum}`)
        targetElement.remove()
        questionsNum -= 1;
    }
})

function addNewAnswerEventHandler(item) {
    item.addEventListener('click', () => {
        const answer = `<div class="answer"><input type="radio" name="${item.parentElement.nextElementSibling.getAttribute("class")}" required> <input type="text" required></div>`;
        item.parentElement.nextElementSibling.innerHTML += answer;
    })
}

function addDeleteAnswerEventHandler (item) {
    item.addEventListener('click', () => {
        const answer = item.parentElement.nextElementSibling.children[item.parentElement.nextElementSibling.children.length - 1];
        if (item.parentElement.nextElementSibling.children.length === 2) {
            alert("At least two options are required");
        } else {
            answer.remove()
        }
    });
}

myForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const requestData = [];
    if (myForm.checkValidity()) {
        const formData = new FormData(myForm);
        for (const pair of formData.entries()) {
            requestData[pair[0]] = pair[1]
        }
        const questions = document.querySelectorAll("#questionsContainer > div");
        for (const question of questions) {
            const questionSummary = {body: '', answers: []};
            questionSummary.body = question.firstElementChild.firstElementChild.value;
            for (const answer of question.lastElementChild.children) {
                questionSummary.answers.unshift({"body": answer.lastElementChild.value, "status": answer.firstElementChild.checked});
            }
            requestData.questions.unshift(questionSummary);
        }
    }

    fetch('http://localhost:5001/api/v1/quizzes', {
        method: 'POST',
        body: JSON.stringify(requestData),
        headers: {"Content-Type": "application/json"},
        credentials : "include",
    }).then(res => {
        if (res.ok) {
            document.location = "/index.html";
        } else {
            // Show error page
            showErrorPage(res);
        }
    });
  })
