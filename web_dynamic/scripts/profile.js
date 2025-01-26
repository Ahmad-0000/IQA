// Populating profile page
const errorPage = document.querySelector("#error");
const errorCode = document.querySelector("#error h1 span");
const errorMessage = document.querySelector("#error p:first-of-type");
const url = new URL(location.href);
const userId = url.searchParams.get("user_id");
const namePlace = document.querySelector(".personal-info p:first-of-type");
const dob = document.querySelector(".personal-info p:nth-child(2) span");
const joinDate = document.querySelector(".personal-info p:nth-child(3) span");
const quizzesNumber = document.querySelector(".personal-info p:last-of-type span");
const bio = document.querySelector(".personal-info textarea");
const updateTriggers = document.querySelectorAll(".update-trigger");
const updateForm = document.querySelector("form");
let userData = undefined;

// Handle error response
async function showErrorPage(res) {
  // Show the error page
  errorPage.style.display = "flex";
  const data = await res.json();
  errorCode.textContent = res.status;
  errorMessage.textContent = data.error;
}

for (const trigger of updateTriggers) {
    trigger.addEventListener('click', function () {
        updateForm.style.zIndex = "10";
        updateForm.children[1].value = userData.first_name;
        updateForm.children[2].value = userData.bio;
    });
}

updateForm.children[0].addEventListener('click', function () {
    updateForm.style.zIndex = "-1";
});

if (userId === null || userId === "me") {
    fetch(`http://localhost:5001/api/v1/users/me`).then((res) => {
        if (res.status === 200) {
            return res.json();
        } else {
            showErrorPage(res);
        }
    })
      .then((data) => {
        namePlace.children[0].textContent = data.first_name;
        namePlace.textContent = `${data.middle_name} ${data.last_name}`;
        dob.textContent = data.dob;
        joinDate.textContent = data.added_at;
        quizzesNumber.textContent = "To be implemented";
        bio.value = data.bio;
      });
} else {
    fetch(`http://localhost:5001/api/v1/users?user_id=${userId}`).then((res) => {
        if (res.status === 200) {
            return res.json();
        } else {
            showErrorPage(res);
        }
    })
      .then((data) => {
        userData = data;
        namePlace.children[0].textContent = data.first_name;
        namePlace.append(`${data.middle_name} ${data.last_name}`);
        dob.textContent = data.dob;
        joinDate.textContent = data.added_at;
        quizzesNumber.textContent = "To be implemented";
    })
}

updateForm.addEventListener('submit', function (event) {
    event.preventDefault();
    const data = {};
    if (updateForm.checkValidity()) {
        const formData = new FormData(updateForm);
        for (const pair of formData.entries()) {
            data[pair[0]] = pair[1];
        }
        if (data.first_name === userData.first_name && data.bio === userData.bio && data.password === "") {
            alert('Provide at least one new value');
        } else {
            fetch(`http://localhost:5001/api/v1/users?user_id=${userData.id}`, {
                method: 'PUT',
                headers: {'content-type': 'application/json'},
                body: JSON.stringify(data),
                credentials: 'include'
            }).then(res => {
                if (res.ok) {
                    return res.json();
                } else {
                    showErrorPage(res);
		    throw new Error();
                }
            }).then(data => {
		    console.log(data)
                userData = data;
                namePlace.children[0].textContent = data.first_name;
                bio.value = data.bio;
            }, () => {});
        }
    }
});

errorPage.children[0].addEventListener('click', () => {
    errorPage.style.display = "none";
  })