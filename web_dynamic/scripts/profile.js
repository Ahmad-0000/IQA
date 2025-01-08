// Populating profile page
const errorPage = document.querySelector("#error");
const errorCode = document.querySelector("#error h1 span");
const errorMessage = document.querySelector("#error p:first-of-type");
const url = new URL(location.href);
const userId = url.searchParams.get("user_id");
const namePlace = document.querySelector(".personal-info p:first-of-type");
const dob = document.querySelector(".personal-info p:nth-child(2)");
const joinDate = document.querySelector(".personal-info p:nth-child(3)");
const quizzesNumber = document.querySelector(".personal-info p:last-of-type");
const bio = document.querySelector(".personal-info textarea");

if (userId === null || userId === "me") {
    fetch(`http://localhost:5001/api/v1/users/me`).then((res) => {
        if (res.status === 200) {
            return res.json();
        } else {
            showErrorPage(res);
        }
    })
      .then((data) => {
        namePlace.textContent += `${data.first_name} ${data.middle_name} ${data.last_name}`;
        dob.textContent += data.dob;
        joinDate = data.added_at;
        quizzesNumber = "To be implemented";
      });
} else {
    fetch(`http://localhost:5001/api/v1/users/${userId}`).then((res) => {
        if (res.status === 200) {
            return res.json();
        } else {
            showErrorPage(res);
        }
    })
      .then((data) => {
        namePlace.textContent += `${data.first_name} ${data.middle_name} ${data.last_name}`;
        dob.textContent += data.dob;
        joinDate = data.added_at;
        quizzesNumber = "To be implemented"; 
    })
}

async function showErrorPage(response) {
    // Show the error page
    errorPage.style.display = "flex";
    const data = await response.json();
    errorCode.textContent = data.status;
    errorMessage.textContent = data.body;
}
