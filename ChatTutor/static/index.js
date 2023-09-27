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

  fetch('/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(args)
  }).then(response => {
    const reader = response.body.getReader();
    let accumulatedContent = "";
    let isFirstMessage = true;
    function read() {
      reader.read().then(({ done, value }) => {
        if (done) {
          // Enable the send button when streaming is done
          sendBtn.disabled = false;
          return;
        }
        const strValue = new TextDecoder().decode(value);
        const messages = strValue.split('\n\n').filter(Boolean).map(chunk => JSON.parse(chunk.split('data: ')[1]));
        messages.forEach(message => {
          const contentToAppend = message.message.content ? message.message.content : "";

          accumulatedContent += contentToAppend;

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
        sendBtn.disabled = false;
      });
    }
    read();
  }).catch(err => {
    console.error('Fetch error:', err);
    // Enable the send button in case of an error
    sendBtn.disabled = false;
  });
}

function updateLastMessage(newContent) {
  if (lastMessageId) {
    const lastMessageElement = document.querySelector(`#${lastMessageId} .msg-text`);
    
    if (lastMessageElement) {
      lastMessageElement.innerHTML = newContent;
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

  const msgHTML = `
    <div class="msg ${side}-msg" id="${messageId}">
      <div class="msg-img" style="background-image: url(${img})"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${role_name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">${message}</div>
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
