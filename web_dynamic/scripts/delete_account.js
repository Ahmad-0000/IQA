// Delete a user's account
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

  form.addEventListener('submit', function (event) {
    event.preventDefault();

    if (form.checkValidity()) {
        const formData = new FormData(form);
        for (const pair of formData.entries()) {
            requestData[pair[0]] = pair[1];
            fetch(`http://localhost:5001/api/v1/users`, {
                method: 'DELETE',
                body: JSON.stringify(requestData),
                headers: {'content-type': 'application/json'},
                credentials: 'include'
            }).then(res => {
                if (res.ok) {
                    window.location = '/index.html';
                } else {
                    showErrorPage(res);
                    throw new Error();
                }
            }).catch((error) => {})
        }
    }
})

// Hide error page
errorPage.children[0].addEventListener('click', () => {
    errorPage.style.display = "none";
  })