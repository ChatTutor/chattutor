// Constants for embed mode and UI elements
import {lightMode, darkMode, setProperties} from "./constants.js";
import {alert} from "./nicealert.js"
import { clearFileInput } from "./fileupload.js";
// import { setFromDoc, clearFromDoc } from "./from_doc_ext.js";
const embed_mode = false;
const clear = document.getElementById('clearBtnId');
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
var stopGeneration = false
let selectedModel = document.getElementById('modelDropdown').value

// Get the send button
const sendBtn = document.getElementById('sendBtn');
const themeBtn = document.getElementById('themeBtn')
const themeBtnDiv = document.getElementById('themeBtnDiv')
const messageInput = document.getElementById('msgInput')
const scrollHelper = document.getElementById('scrollHelper')
const stopGenButton = document.getElementById('stopBtnId')
const uploadZipButton = document.getElementById('uploadBtnId')
const sendUploadedZipButton = document.getElementById('sendformupload')
const uploadZipPapersForm = document.getElementById('uploadFileForm')
const selectUploadedCollection = document.getElementById('selectUploadedCollection')
const clearformupload = document.getElementById("clearformupload")
const modelDropdown = document.getElementById('modelDropdown')

let uploadedCollections = []
messageInput.addEventListener('input', (event) => {
  console.log('kajk')
  sendBtn.disabled = messageInput.value.length === 0;
})

stopGenButton.style.display = 'none'
// Listen for windoe resize to move the 'theme toggle button
window.addEventListener('resize', windowIsResizing)

function windowIsResizing() {
  console.log("resize")
    // the button for choosing themes snaps in place when the window is too small
  if(window.innerWidth < 1200) {
      themeBtnDiv.style.position = 'inherit'
      themeBtnDiv.style.top = '25px'
      themeBtnDiv.style.left = '25px'

      const arr = document.querySelectorAll('.theme-button')
      console.log(arr)
      arr.forEach(btn => {
        btn.style.backgroundColor = 'transparent'
        btn.style.color = 'var(--msg-header-txt)'
        btn.style.textDecoration = 'underline'
        btn.style.padding = '0'
        btn.style.boxShadow = 'none'
        btn.style.border = 'none'
        btn.style.borderRadius = '0px'
        btn.style.margin = '0'

        btn.style.height = 'unset'
        btn.style.width = 'unset'
      })

  } else {
      themeBtnDiv.style.position = 'fixed'
      themeBtnDiv.style.top = '25px'
      themeBtnDiv.style.left = '25px'
      const arr = document.querySelectorAll('.theme-button')
      console.log(arr)
      arr.forEach(btn => {
        btn.style.backgroundColor = 'rgb(140, 0, 255)'
        btn.style.color = 'white'
        btn.style.textDecoration = 'none'
        btn.style.padding = '10px'
        btn.style.boxShadow = '0 5px 5px -5px rgba(0, 0, 0, 0.2)'
        btn.style.border = 'var(--border)'
        btn.style.borderRadius = '50%'
        btn.style.margin = '0'
        btn.style.height = '40px'
        btn.style.width = '40px'
      })
  }
}

function getFormattedIntegerFromDate() {
    let d = Date.now()

}

const smallCard = {
  card_max_width: '867px'
}

const bigCard = {
  card_max_width: 'unset'
}

let theme = null
let interfaceTheme = null

// Configures UI
if(embed_mode) {
  setupEmbedMode();
}

function uploadMessageToDB(msg, chat_k) {
    if(msg.content === "") {
        return
    }
    const data_ = {content: msg.content, role: msg.role, chat_k: chat_k, time_created: `${Date.now()}`, clear_number: getClearNumber()}
    console.log(`DATA: ${JSON.stringify(data_)} `)
    fetch('/addtodb', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data_)})
        .then(() =>{
            console.log('Andu')
        })
}

// Event listener to clear conversation
clear.addEventListener('click', clearConversation);

// Event listener to handle form submission
msgerForm.addEventListener("submit", handleFormSubmit);

// Event listener to load conversation from local storage on DOM load
document.addEventListener("DOMContentLoaded", loadConversationFromLocalStorage);
// REMVE ALL from collections saved in local storage + clean up local storage
document.addEventListener("DOMContentLoaded", clearCollectionsFromLocalStorage)

document.addEventListener('DOMContentLoaded', setThemeOnRefresh)

document.addEventListener('DOMContentLoaded', windowIsResizing)

// Event listener for toggling the theme
themeBtn.addEventListener('click', toggleDarkMode)

stopGenButton.addEventListener('click', stopGenerating)

modelDropdown.addEventListener('change', handleModelDropdownChange);

function handleModelDropdownChange(event) {
  selectedModel = event.target.value;
  console.log("Selected model:", selectedModel);
}



// I dodn't know if i should install uuidv4 using npm or what should i use
function uuidv4() {
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

function setChatId() {
    localStorage.setItem('conversation_id', uuidv4())
}

function getChatId() {
    return localStorage.getItem('conversation_id')
}

function increaseClearNumber() {
    let clnr = getClearNumber()
    let clear_number = parseInt(clnr)
    localStorage.setItem('clear_number', `${clear_number+1}`)
}

function resetClearNumber() {
    localStorage.setItem('clear_number', '0')
}

function getClearNumber() {
    return localStorage.getItem('clear_number')
}

function reinstantiateChatId() {
    increaseClearNumber()
}

// function for keeping the theme whn the page refreshes
function setThemeOnRefresh() {
  // disable send button
  sendBtn.disabled = messageInput.value.length === 0;
  if(getChatId() == null) {
    setChatId()
  }

  if(getClearNumber() == null) {
      resetClearNumber()
  }

  theme = localStorage.getItem('theme')
  if (theme == null) {
    setTheme('dark')
  } else {
    setTheme(theme)
  }

  interfaceTheme = 'normal'
  setTheme('normal')

}
// helper function
function setTheme(th) {
  setProperties()
  const _style = "\"font-size: 15px !important; padding: 0 !important; margin: 0 !important; vertical-align: middle\""
    themeBtn.innerHTML = theme === "dark" ? `<span class="material-symbols-outlined" style=${_style}> light_mode </span>` :
        `<i class="material-symbols-outlined" style=${_style}> dark_mode\n </i>`
}

// function that toggles theme
function toggleDarkMode() {
  if (theme === 'light') {
    theme = 'dark'
  } else if(theme === 'dark') {
    theme = 'light'
  } else {
    theme = 'dark'
  }
  localStorage.setItem('theme', theme)
  setTheme(theme)
}

function toggleInterfaceMode() {
  interfaceTheme = 'normal'
  localStorage.setItem('interfacetheme', interfaceTheme)
  setTheme(interfaceTheme)

}

function clearConversation() {
  conversation = [];
  localStorage.setItem("cqn-conversation", JSON.stringify([]));
    reinstantiateChatId()
  var childNodes = msgerChat.childNodes;
  for(var i = childNodes.length - 3; i >= 2; i--){
      var childNode = childNodes[i];
      if (childNode.id !== 'clearContId' && childNode.id !== 'clearBtnId') {
        childNode.parentNode.removeChild(childNode);
      }
  }
  sendBtn.disabled = false;
}

function stopGenerating() {
  stopGeneration = true
}

function handleFormSubmit(event) {
  event.preventDefault();
  const msgText = msgerInput.value;
  if (!msgText) return;
  // if (selectUploadedCollection && !selectUploadedCollection.options[ selectUploadedCollection.selectedIndex ]) {
  //   alert("Please upload some files for the tutor to learn from!")
  //   return
  // }

  // Disable the send button
  sendBtn.disabled = true;
  clear.style.display = 'none'
  stopGenButton.style.display = 'block'

  addMessage("user", msgText, true);
  uploadMessageToDB({role: 'user', content: msgText}, getChatId())
  msgerInput.value = "";
  queryGPT();
}


function loadConversationFromLocalStorage() {
  conversation = JSON.parse(localStorage.getItem("cqn-conversation"))
  if(conversation){
    conversation.forEach(message => {
      addMessage(message["role"], message["content"], false)
      if (message["context_documents"]) {
        setLatMessageHeader(message["context_documents"])

      }
    })
  }
  else conversation = []
  MathJax.typesetPromise();
}

function loadCollectionsFromLocalStorage() {
  collections = JSON.parse(localStorage.getItem("uploaded-collections"))//TODO
  if(collections) {
    collections.forEach(collname => {
      addCollectionToFrontEnd(collname)
    })
  }
}

function clearCollectionsFromLocalStorage() {
  let collections = JSON.parse(localStorage.getItem("uploaded-collections"))
  if(collections) {
    collections.forEach(collname => {
      fetchClearCollection(collname)
    })
  }
}

function fetchClearCollection(collname) {
  console.log("clearing ", collname)
  let args = {
    "collection":collname
  }
  fetch("/delete_uploaded_data", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(args)
  }).then(response => response.json()).then(data => {
    console.log("deleted " + data["deleted"])
  })
}




function queryGPT(fromuploaded=false, uploaded_collection_name="test_embedding") {
  let collection_name = "test_embedding"
  let selected_collection_name = "test_embedding"
  // if (selectUploadedCollection && !selectUploadedCollection.options[ selectUploadedCollection.selectedIndex ]) {
  //   alert("Please upload some files for the tutor to learn from! Click on menu!")
  //   return
  // }
  if (selectUploadedCollection.options.length > 0) {
    selected_collection_name = selectUploadedCollection.options[ selectUploadedCollection.selectedIndex ].value
  }
  const args = {
    "conversation": conversation,
    "multiple": true,
    "collection": [collection_name, selected_collection_name]
  }
  if (embed_mode) args.from_doc = original_file
  if (READ_FROM_DOC != null) args.from_doc = READ_FROM_DOC

  args.selectedModel = selectedModel

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
    let context_documents = null;
    function read() {
      reader.read().then(({ done, value }) => {
        if (done) {
          // Enable the send button when streaming is done
          sendBtn.disabled = false;
          clear.style.display = 'block'
          stopGenButton.style.display = 'none'
          stopGeneration = false
            uploadMessageToDB({content: accumulatedContent, role: 'assistant'}, getChatId())
          return;
        }
        const strValue = new TextDecoder().decode(value);
        const messages = strValue.split('\n\n').filter(Boolean).map(chunk => JSON.parse(chunk.split('data: ')[1]));
          let message;
          for (var messageIndex in messages) {
              message = messages[messageIndex]
              if (stopGeneration === false) {
                  if (message.message.valid_docs) {
                    context_documents = message.message.valid_docs
                    console.log(context_documents)
                  }
                  const contentToAppend = message.message.content ? message.message.content : "";
                  accumulatedContent += contentToAppend;
              }
              if (isFirstMessage) {
                console.log("added", accumulatedContent)
                addMessage("assistant", accumulatedContent, false);
                setLatMessageHeader(context_documents)
                isFirstMessage = false;
              } else {
                console.log('message',message.message)
                  if (typeof (message.message.content) == 'undefined') {
                      conversation.push({"role": 'assistant', "content": accumulatedContent, "context_documents" : context_documents})
                      localStorage.setItem("cqn-conversation", JSON.stringify(conversation))
                  }
                  console.log("updated", accumulatedContent)

                  scrollHelper.scrollIntoView()
                  updateLastMessage(accumulatedContent);

                  if (message.message.error) {
                    conversation.push({"role": 'assistant', "content": accumulatedContent})
                    localStorage.setItem("cqn-conversation", JSON.stringify(conversation))
                  }
              }
              if (stopGeneration === true) {
                  accumulatedContent += " ...Stopped generating";
                  conversation.push({"role": 'assistant', "content": accumulatedContent})
                  localStorage.setItem("cqn-conversation", JSON.stringify(conversation))
                  sendBtn.disabled = false;
                  clear.style.display = 'block'
                  stopGenButton.style.display = 'none'
                  uploadMessageToDB({content: accumulatedContent, role: 'assistant'}, getChatId())
                  scrollHelper.scrollIntoView()
                  updateLastMessage(accumulatedContent);
                  break
              }
          }
        if(stopGeneration === false) {
          read();
        } else {
          stopGeneration = false
        }
      }).catch(err => {
        console.error('Stream error:', err);
        sendBtn.disabled = false;
        clear.style.display = 'block'
        stopGenButton.style.display = 'none'
        stopGeneration = false
      });
      MathJax.typesetPromise();
    }
    read();
    // MathJax.typesetPromise();
  }).catch(err => {
    console.error('Fetch error:', err);
    // Enable the send button in case of an error
    sendBtn.disabled = false;
    clear.style.display = 'block'
    stopGenButton.style.display = 'none'
    stopGeneration = false
  });
}

function formatMessage(message, makeLists = true) {
  const messageArr = message.split("\n")

  let messageStr = ""
  let listSwitch = 0
  for (let messageArrIndex in messageArr) {
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



function setLatMessageHeader(context_documents) {
  // Remove duplicates
  context_documents = context_documents.filter((value, index, self) => 
      self.map(item => item.metadata.docname).indexOf(value.metadata.docname) === index
  );
  if (lastMessageId) {
    const lastMessageElement = document.querySelector(`#${lastMessageId} .msg-text`);
    if (lastMessageElement) {
      var docs = ''
      context_documents.forEach(doc => {
        docs += `<div class="msg-context-doc col ${lastMessageId}-context" data-doc="${doc.metadata.doc}">
          <div style="align-self: self-start;">
            <span>${doc.metadata.doc}</span>
          </div>

          <div class="info col">
            <div>
              <div class="askmore context-info col" onclick='setFromDoc(${JSON.stringify(doc.metadata)})'>Ask about</div>
              <div class="inform context-info col" onclick='setDocInfo(${JSON.stringify(doc.metadata)})'>Info</div>
            </div>
          </div>
        </div>`
      })

      document.querySelector(`#${lastMessageId}`).innerHTML = `
        <div class="msg-header-context">${docs}</div>
        ${document.querySelector(`#${lastMessageId}`).innerHTML}
      `;
    } else {
      console.error('Cannot find the .msg-text element to update.');
    }
  } else {
    console.error('No message has been added yet.');
  }
}

function updateLastMessage(newContent) {
  if (lastMessageId) {
    const lastMessageElement = document.querySelector(`#${lastMessageId} .msg-text`);
    if (lastMessageElement) {
      const newContentFormatted = formatMessage(newContent)
      document.querySelector(`#${lastMessageId} .msg-text`).innerHTML = newContentFormatted;
    } else {
      console.error('Cannot find the .msg-text element to update.');
    }
  } else {
    console.error('No message has been added yet.');
  }
  // MathJax.typesetPromise();

}

clearformupload.addEventListener("click", ()=>{
  clearFileInput(document.querySelector("#upload"))
})



function addMessage(role, message, updateConversation) {
    let role_name
    let img
    let side

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
    <div class="msg-bgd">
      <div class="msg-img" style="background-image: url(${img})"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${role_name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">${messageStr}</div>
      </div>
      </div>
    </div>
  `;

  clearContainer.insertAdjacentHTML("beforebegin", msgHTML);

  // Find the newly added message and animate it
  const newMessage = document.getElementById(messageId);
  newMessage.style.opacity = "0";
  newMessage.style.transform = "translateY(1rem)";

  // MathJax.typesetPromise([newMessage]);
  
  // Trigger reflow to make the transition work
  void newMessage.offsetWidth;
  
  // Start the animation
  newMessage.style.opacity = "1";
  newMessage.style.transform = "translateY(0)";
  msgerChat.scrollTop += 500;
  if(updateConversation){
    conversation.push({"role": role, "content": message})
    localStorage.setItem("cqn-conversation", JSON.stringify(conversation))
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


export function uploadFile() {
  let myFormData = new FormData(uploadZipPapersForm)
  const formDataObj = {};
  myFormData.forEach((value, key) => (formDataObj[key] = value));
  console.log(formDataObj)

  sendUploadedZipButton.querySelector("span").innerHTML = `<img src="./images/loading.gif" style="width: 40px; height: 40px;">`

  console.log(formDataObj["file"])
  if (formDataObj["file"]["name"] == '') {
    alert("Please upload a file!")
    sendUploadedZipButton.querySelector("span").innerHTML = "upload"

    return
  }

  fetch('/upload_data_to_process', {
    method: 'POST',
    body: new FormData(uploadZipPapersForm)
  }).then(response => response.json()).then(data => {
    let created_collection_name = data['collection_name']
    console.log("Created collection " + created_collection_name)
    if (created_collection_name == false || created_collection_name == "false") {
      alert("Select file")
    } else {
      addCollectionToFrontEnd(created_collection_name)

    }



    sendUploadedZipButton.querySelector("span").innerHTML = "upload"
    clearFileInput(document.querySelector("#upload"))
  })
}

function addCollectionToFrontEnd(created_collection_name) {
  uploadedCollections.push(created_collection_name)
  console.log(uploadedCollections)
    selectUploadedCollection.innerHTML += `
      <option value=${created_collection_name}>${created_collection_name.split("_")[0]}:collection</option>
    `
    localStorage.setItem("uploaded-collections", JSON.stringify(uploadedCollections))
  alert(`Created collection ${created_collection_name}`)
}

if (sendUploadedZipButton)
sendUploadedZipButton.addEventListener("click", uploadFile)


function hasClass(ele, cls) {
  return !!ele.className.match(new RegExp('(\\s|^)' + cls + '(\\s|$)'));
}

function addClass(ele, cls) {
  if (!hasClass(ele, cls)) ele.className += " " + cls;
}

function removeClass(ele, cls) {
  if (hasClass(ele, cls)) {
      var reg = new RegExp('(\\s|^)' + cls + '(\\s|$)');
      ele.className = ele.className.replace(reg, ' ');
  }
}

//Add event from js the keep the marup clean
function init() {
  document.getElementById("open-menu").addEventListener("click", toggleMenu);
  document.getElementById("body-overlay").addEventListener("click", toggleMenu);
}

//The actual fuction
function toggleMenu() {
  var ele = document.getElementsByTagName('body')[0];
  if (!hasClass(ele, "menu-open")) {
      addClass(ele, "menu-open");
  } else {
      removeClass(ele, "menu-open");
  }
}

//Prevent the function to run before the document is loaded
document.addEventListener('readystatechange', function() {
  if (document.readyState === "complete") {
      init();
  }
});



document.querySelector(".close-notif").addEventListener('click', e => {
  clearFromDoc();
})



document.querySelector(".close-arxiv").addEventListener('click', e => {
  clearDocInfo();
})

