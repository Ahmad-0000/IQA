// Handle registeration

const fName = document.querySelector("#f-name")
const mName = document.querySelector("#m-name")
const lName = document.querySelector("#l-name")
const email = document.querySelector("#email")
const password = document.querySelector("#password")
const dob = document.querySelector("#dob")
const myForm = document.querySelector("form")

myForm.addEventListener('submit', (event) => {

  // Prevent the default action of form submission
  event.preventDefault();

  if (myForm.checkValidity()) {
    const formData = new FormData(myForm);
    const data = {};
    formData.forEach((name, value) => {
      data[name] = value;
    });
    fetch("http://localhost:5001/api/v1/users", {
      method: 'POST',
      headers: 'Content-Type: application/json',
      body: JSON.stringify(body),
      credentials: 'include',
    }).then((res) => {
      if (res.ok && res.status === 201) {
        document.location = "/profile.html";
      } else {
        if (res.status === 409) {
          conosle.log(`${data.email} was taken`);
	} else if (res.status === 400) {
          console.log("Abide to data constraints");
	}
      }
    });
  }
});
