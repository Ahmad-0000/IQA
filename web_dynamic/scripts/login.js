// Handle logging in
const errorPage = document.querySelector("#error");
const errorCode = document.querySelector("#error h1 span");
const errorMessage = document.querySelector("#error p:first-of-type");
const form = document.querySelector("form");
const submit = document.querySelector("#submit");
const requestData = {};


// Handle error response
async function showErrorPage(res) {
    // Show the error page
    errorPage.style.display = "flex";
    const data = await res.json();
    errorCode.textContent = res.status;
    errorMessage.textContent = data.error;
  }

submit.addEventListener('click', function (event) {
    event.preventDefault();

    if (form.checkValidity()) {
        const formData = new FormData(form);
        for (const pair of formData.entries()) {
            requestData[pair[0]] = pair[1];
            fetch('http://localhost:5001/api/v1/login', {
                method: 'POST',
                body: JSON.stringify(requestData),
                headers: {'content-type': 'application/json'},
                credentials: 'include'
            }).then(res => {
                if (res.ok) {
                    return res.json();
                } else {
                    showErrorPage(res);
                    throw new Error();
                }
            }).then((data) => {
                window.location = `/profile.html?user_id=~${data.id}`;
            }, (error) => {});
        }
    }
})
