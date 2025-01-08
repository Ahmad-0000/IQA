// Handle registeration

const fName = document.querySelector("#f-name")
const mName = document.querySelector("#m-name")
const lName = document.querySelector("#l-name")
const email = document.querySelector("#email")
const password = document.querySelector("#password")
const dob = document.querySelector("#dob")
const registerBtn = document.querySelector("#submit")

registerBtn.addEventListener('click', () => {
  const data = {
    "first_name": fName.value,
    "middle_name": mName.value,
    "last_name": lName.value,
    "email": email.value,
    "password": password.value,
    "dob": dob.value,
    "agree": agree.checked
  }
  fetch("http://localhost:5001/api/v1/users", {
    method: 'POST',
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
    credentials: "include",
  }).then((res) => {
    console.log(res);
    if (res.ok) {
      document.location = "/profile.html";
    } else {
      res.json();
    }
  }).then((data) = > {console.log(data)});
});
