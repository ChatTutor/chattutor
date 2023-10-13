var READ_FROM_DOC = null
var READ_FROM_DOC_META = null
var DOC_INFO = null
function setFromDoc(doc) {
    setDocInfo(doc)
    READ_FROM_DOC_META = doc
    doc = doc.doc
    READ_FROM_DOC = doc
    document.querySelector("#from-doc").innerHTML = READ_FROM_DOC
    document.querySelector(".notification").classList.remove("hiddenop")
    document.querySelector(".notification").classList.add("hidden")

    document.querySelector(".msger-input").value = `Please tell me more about "${READ_FROM_DOC}".`
    document.querySelector("#sendBtn").disabled = false
  }
  
function clearFromDoc() {
    READ_FROM_DOC = null
    READ_FROM_DOC_META = null
    document.querySelector("#from-doc").innerHTML = ""
    document.querySelector(".notification").classList.add("hiddenop")
  }


  function setDocInfo(doc) {
    DOC_INFO = doc
    console.log(DOC_INFO)
    document.querySelector("#arxiv-doc").innerHTML = format_docinfo(DOC_INFO)
    document.querySelector(".arxiv-info").classList.remove("hiddenop")
    document.querySelector(".arxiv-info").classList.remove("hidden")
  }

function format_docinfo(docinfo) {
    if (docinfo.entry_id)
        return `
            <div markdown="1" class="arxiv-docinfo">
                <h3>${docinfo.title}</h3>
                <div class="categories">${docinfo.categories}</div>
                <br/>
                <div>Url : <a href = ${docinfo.entry_id}>${docinfo.entry_id}</a> </div>
                <br/>

                <div>Authors : ${docinfo.authors}</div>
                <br/>

                <div>Published in ${docinfo.published} </div>
                <br/>

                <div>DOI : ${docinfo.doi}</div>
            </div>
        `
    return `
        <div markdown="1" class="arxiv-docinfo">
            <h3>${docinfo.doc}</h3>
        </div>
    `
}
  
function clearDocInfo() {
    DOC_INFO = null
    document.querySelector("#arxiv-doc").innerHTML = ""
    document.querySelector(".arxiv-info").classList.add("hiddenop")

    if (READ_FROM_DOC_META ) {
        setDocInfo(READ_FROM_DOC_META)
    }
  }

