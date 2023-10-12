var READ_FROM_DOC = null
function setFromDoc(doc) {
    READ_FROM_DOC = doc
    document.querySelector("#from-doc").innerHTML = READ_FROM_DOC
    document.querySelector(".notification").classList.remove("hiddenop")
  }
  
function clearFromDoc() {
    READ_FROM_DOC = null
    document.querySelector("#from-doc").innerHTML = ""
    document.querySelector(".notification").classList.add("hiddenop")
  }
