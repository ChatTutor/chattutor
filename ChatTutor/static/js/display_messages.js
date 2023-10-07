const subBtn = document.getElementById("subBtn")
const usernameInput = document.getElementById("lusername")
const passcodeInput = document.getElementById("lpassword")
const sqlInput = document.getElementById("lexesql")
const consoleID = document.getElementById("consoleID")
const showBtn = document.getElementById("showBtn")
const inputArea = document.getElementById('sqlinputarea')
async function submitButtonClicked() {
    let data = {lusername: usernameInput.value, lpassword: passcodeInput.value, lexesql: sqlInput.value}
    const headers = {
        'Content-Type': 'application/json',
    };
    console.log(data)
    let response = await fetch('/exesql', {method: "POST", headers: headers, body: JSON.stringify(data)})
    let text = await response.text()
    console.log(text)
    consoleID.innerText = text
}

function toggleHidden() {
    let display = inputArea.style.display
    inputArea.style.display = display === 'none' ? 'flex' : 'none'
}
showBtn.addEventListener('click', toggleHidden)

subBtn.addEventListener('click', submitButtonClicked)
