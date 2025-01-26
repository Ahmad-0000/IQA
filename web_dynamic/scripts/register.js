// Handle registeration

const errorPage = document.querySelector("#error");
const errorCode = document.querySelector("#error h1 span");
const errorMessage = document.querySelector("#error p:first-of-type");
const fName = document.querySelector("#f-name")
const mName = document.querySelector("#m-name")
const lName = document.querySelector("#l-name")
const email = document.querySelector("#email")
const password = document.querySelector("#password")
const dob = document.querySelector("#dob")
const myForm = document.querySelector("form")
const data = {};

myForm.addEventListener('submit', (event) => {

  // Prevent the default action of form submission
  event.preventDefault();

  if (myForm.checkValidity()) {
    const formData = new FormData(myForm);
    for (const pair of formData.entries()) {
      data[pair[0]] = pair[1];
    }
    data['agree'] = true;
    fetch("http://localhost:5001/api/v1/users", {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data),
      credentials: 'include',
    }).then((res) => {
          if (res.ok) {
            return res.json();
          } else {
            showErrorPage(res);
          }
      }).then((data) => {
          document.location = `/profile.html?user_id=${data.id}`;
      });
  }
});

async function showErrorPage(res) {
  // Show the error page
  errorPage.style.display = "flex";
  const data = await res.json();
  errorCode.textContent = res.status;
  errorMessage.textContent = data.error;
}

errorPage.children[0].addEventListener('click', () => {
  errorPage.style.display = "none";
})
