// Constants for embed mode and UI elements
const embed_mode = false;
const clear = get('.clear-btn');
const clearContainer = get('.clear-btn-container');
const mainArea = get('.msger');
const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");


// Constants for bot and person details
const BOT_IMG = "https://static.thenounproject.com/png/2216285-200.png";
const PERSON_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/1024px-Default_pfp.svg.png";
const BOT_NAME = "ChatTutor";
const PERSON_NAME = "Student";

// URLs for production and debugging
const prodAskURL = new URL("https://chattutor-393319.ue.r.appspot.com/ask");
const debugAskURL = new URL("http://127.0.0.1:5000/ask");

// Variables to hold conversation and message details
var conversation = [];
var original_file = "";
let lastMessageId = null;

// Get the send button
const sendBtn = document.getElementById('sendBtn');
const themeBtn = document.getElementById('themeBtn')




// Listen for windoe resize to move the 'theme toggle button
window.addEventListener('resize', windowIsResizing)

function windowIsResizing() {
    // the button for choosing themes snaps in place when the window is too small
  if(window.innerWidth < 1200) {
      themeBtn.style.backgroundColor = 'transparent'
      themeBtn.style.position = 'inherit'
      themeBtn.style.color = 'var(--msg-header-txt)'
      themeBtn.style.textDecoration = 'underline'
      themeBtn.style.top = '25px'
      themeBtn.style.left = '25px'
      themeBtn.style.padding = '0'
      themeBtn.style.boxShadow = 'none'
      themeBtn.style.border = 'none'
      themeBtn.style.borderRadius = '0px'
  } else {
      themeBtn.style.backgroundColor = 'var(--right-msg-bg)'
      themeBtn.style.position = 'fixed'
      themeBtn.style.color = 'white'
      themeBtn.style.textDecoration = 'none'
      themeBtn.style.top = '25px'
      themeBtn.style.left = '25px'
      themeBtn.style.padding = '15px 10px'
      themeBtn.style.boxShadow = '0 5px 5px -5px rgba(0, 0, 0, 0.2)'
      themeBtn.style.border = 'var(--border)'
    themeBtn.style.borderRadius = '20px'
  }
}
// Themes
const lightMode = {
  body_bg: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
  msger_bg: '#fff',
  border: '1px solid #ddd',
  left_msg_bg: '#ececec',
  left_msg_txt: 'black',
  right_msg_bg: '#579ffb',
  msg_header_bg: 'rgba(238,238,238,0.75)',
  msg_header_txt: '#666',
  clear_btn_txt: '#999',
  msg_chat_bg_scrollbar: '#ddd',
  msg_chat_bg_thumb: '#bdbdbd',
  msg_chat_bg: '#fcfcfe',
  msg_input_bg: '#ddd',
  msg_input_area_bg: '#eee',
  msg_invert_image: 'invert(0%)',
  msg_input_color: "black"
}

const darkMode = {
  body_bg: 'linear-gradient(135deg, #282828 0%, #17232c 100%)',
  msger_bg: '#2d2d2d',
  border: '1px solid #2d2d2d',
  left_msg_bg: '#383838',
  left_msg_txt: 'white',
  right_msg_bg: '#579ffb',
  msg_header_bg: 'rgba(41,41,41,0.75)',
  msg_header_txt: '#d5d5d5',
  clear_btn_txt: '#e5e5e5',
  msg_chat_bg_scrollbar: '#2d2d2d',
  msg_chat_bg_thumb: '#3f3f3f',
  msg_chat_bg: '#1b1b1b',
  msg_input_bg: '#2f2f2f',
  msg_input_area_bg: '#252525',
  msg_invert_image: 'invert(100%)',
  msg_input_color: "white"
}

let theme = null


// Configures UI
if(embed_mode) {
  setupEmbedMode();
}

// Event listener to clear conversation
clear.addEventListener('click', clearConversation);

// Event listener to handle form submission
msgerForm.addEventListener("submit", handleFormSubmit);

// Event listener to load conversation from local storage on DOM load
document.addEventListener("DOMContentLoaded", loadConversationFromLocalStorage);


document.addEventListener('DOMContentLoaded', setThemeOnRefresh)

document.addEventListener('DOMContentLoaded', windowIsResizing)

// Event listener for toggling the theme
themeBtn.addEventListener('click', toggleDarkMode)

// function for keeping the theme whn the page refreshes
function setThemeOnRefresh() {
  theme = localStorage.getItem('theme')
  if (theme == null) {
    setTheme('light')
  } else {
    setTheme(theme)
  }
}

// helper function
function setTheme(th) {
  const themeObject = theme === 'dark' ? darkMode : lightMode
    for (key in themeObject) {
      const property_replaced = key.replace(/_/g, '-')
      const property_name = `--${property_replaced}`
      console.log(property_name)
      const value = themeObject[key]
      document.documentElement.style.setProperty(property_name, value)
    }
    themeBtn.innerText = theme == "dark" ? "Light mode" : "Dark mode"
}

// function that toggles theme
function toggleDarkMode() {
  if (theme === 'light') {
    theme = 'dark'
  } else if(theme === 'dark') {
    theme = 'light'
  } else {
    theme = 'light'
  }
  setTheme(theme)
  localStorage.setItem('theme', theme)
}

function clearConversation() {
  conversation = [];
  localStorage.setItem("conversation", JSON.stringify([]));

  var childNodes = msgerChat.childNodes;
  for(var i = childNodes.length - 3; i >= 2; i--){
      var childNode = childNodes[i];
      childNode.parentNode.removeChild(childNode);
  }
  sendBtn.disabled = false;
}


function handleFormSubmit(event) {
  event.preventDefault();
  const msgText = msgerInput.value;
  if (!msgText) return;

  // Disable the send button
  sendBtn.disabled = true;

  addMessage("user", msgText, true);
  msgerInput.value = "";
  queryGPT();
}


function loadConversationFromLocalStorage() {
  conversation = JSON.parse(localStorage.getItem("conversation"))
  if(conversation){
    conversation.forEach(message => {addMessage(message["role"], message["content"], false)})
  }
  else conversation = []
  MathJax.typesetPromise();
}

function queryGPT() {
  args = {
    "conversation": conversation,
    "collection": "test_embedding"
  }
  if (embed_mode) args.from_doc = original_file

  fetch(`${window.location.origin}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(args)
  }).then(response => {
    console.log("responded")
    const reader = response.body.getReader();
    let accumulatedContent = "";
    let isFirstMessage = true;
    function read() {
      console.log("reading...")
      reader.read().then(({ done, value }) => {
        if (done) {
          // Enable the send button when streaming is done
          sendBtn.disabled = false;
          return;
        }
        const strValue = new TextDecoder().decode(value);
        console.log(strValue.split('\n[CHUNK]\n').filter(Boolean))
        const messages = strValue.split('\n[CHUNK]\n').filter(Boolean).map(chunk => {
          try {
            return JSON.parse(chunk.split('data: ')[1])
          } catch(e) {
            return {'time': 0, 'message': ''}
          }
        });
        console.log(messages)
        messages.forEach(message => {
          const contentToAppend = message.message.content ? message.message.content : "";
          accumulatedContent += contentToAppend + message.time;
          console.log(accumulatedContent)


          if (isFirstMessage) {
            addMessage("assistant", accumulatedContent, false);
            isFirstMessage = false;
          } else {
            if (typeof(message.message.content) == 'undefined') {
              conversation.push({"role": 'assistant', "content": accumulatedContent})
              localStorage.setItem("conversation", JSON.stringify(conversation))
            }
            updateLastMessage(accumulatedContent);
          }
        });
        read();
      }).catch(err => {
        console.error('Stream error:', err);
        //sendBtn.disabled = false;
        read();
      });
    }
    read();
  }).catch(err => {
    console.error('Fetch error:', err);
    // Enable the send button in case of an error
    sendBtn.disabled = false;
  });
}

function formatMessage(message, makeLists = true) {
  const messageArr = message.split("\n")

  let messageStr = ""
  let listSwitch = 0
  for (messageArrIndex in messageArr) {
    const paragraph = messageArr[messageArrIndex]
    if(paragraph.startsWith('- ') && makeLists) {
      if(listSwitch === 0) {
        messageStr += "<ul style=\"padding-left: 15px !important;\">"
      }

      messageStr += `<li><p>${paragraph.slice(2)}</p></li>`

      listSwitch = 1

    } else if (listSwitch === 1) {
      messageStr += "</ul>"
      messageStr += `<p>${paragraph}</p>`
      listSwitch = 0
    } else {
      messageStr += `<p>${paragraph}</p>`
      listSwitch = 0
    }

  }
  return messageStr
}

function updateLastMessage(newContent) {
  if (lastMessageId) {
    const lastMessageElement = document.querySelector(`#${lastMessageId} .msg-text`);
    
    if (lastMessageElement) {

      const newContentFormatted = formatMessage(newContent)
      lastMessageElement.innerHTML = newContentFormatted;
    } else {
      console.error('Cannot find the .msg-text element to update.');
    }
  } else {
    console.error('No message has been added yet.');
  }
  MathJax.typesetPromise();

}




function addMessage(role, message, updateConversation) {
  if(role === "assistant") {
    role_name = BOT_NAME;
    img = BOT_IMG;
    side = "left";

  }
  else {
    role_name = PERSON_NAME;
    img = PERSON_IMG;
    side = "right";
  }

  const messageId = 'msg-' + new Date().getTime();
  lastMessageId = messageId;

  // if you want to make the robot white ( of course it doesn't work well in safari ), so -- not in use right now
  var invertImage = 'invert(0%)'
  if (side === "left") {
    invertImage = 'var(--msg-invert-image)'
  }

  const messageStr = formatMessage(message, role === "assistant")

  const msgHTML = `
    <div class="msg ${side}-msg" id="${messageId}">
      <div class="msg-img" style="background-image: url(${img})"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${role_name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">${messageStr}</div>
      </div>
    </div>
  `;


  clearContainer.insertAdjacentHTML("beforebegin", msgHTML);
  
  // Find the newly added message and animate it
  const newMessage = document.getElementById(messageId);
  newMessage.style.opacity = "0";
  newMessage.style.transform = "translateY(1rem)";
  
  // Trigger reflow to make the transition work
  void newMessage.offsetWidth;
  
  // Start the animation
  newMessage.style.opacity = "1";
  newMessage.style.transform = "translateY(0)";
  
  msgerChat.scrollTop += 500;
  if(updateConversation){
    conversation.push({"role": role, "content": message})
    localStorage.setItem("conversation", JSON.stringify(conversation))
  }
}


function setupEmbedMode() {
  // Setup minimize and expand buttons to toggle 'minimized' class on mainArea
  const minimize = get('.msger-minimize');
  const expand = get('.msger-expand');
  minimize.addEventListener('click', () => mainArea.classList.toggle('minimized'));
  expand.addEventListener('click', () => mainArea.classList.toggle('minimized'));

  // Extract and store the name of the original file from the 'Download source file' link
  const download_original = document.querySelectorAll('[title="Download source file"]')[0];
  original_file = download_original.getAttribute("href").slice(download_original.getAttribute("href").lastIndexOf("/") + 1);
}


// Utility functions
function get(selector, root = document) {
  return root.querySelector(selector);
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();

  return `${h.slice(-2)}:${m.slice(-2)}`;
}
