const upload_files = document.querySelectorAll('.multiple-upload');

function onFile() {
    console.log(upload.files)
    var me = this,
        file = upload.files[0],
        name = file.name;

    upload.parentNode.querySelector("span").innerHTML = ""
    Array.from(upload.files).forEach(f => {
        var nm = f.name
        if (nm.length > 20) {
            nm = nm.substr(0, 16) + "..."
        }
            
        upload.parentNode.querySelector("span").innerHTML += nm + ", "
    })
}

upload_files.forEach(upload => {
    upload.addEventListener('dragenter', function (e) {
        upload.parentNode.className = 'area dragging';
    }, false);

    upload.addEventListener('dragleave', function (e) {
        upload.parentNode.className = 'area';
    }, false);
    
    upload.addEventListener('dragdrop', function (e) {
        onFile();
    }, false);
    
    upload.addEventListener('change', function (e) {
        onFile();
    }, false);
})

export function clearFileInput(ctrl) {
    try {
        ctrl.value = null;
    } catch(ex) { }
    if (ctrl.value) {
        ctrl.parentNode.replaceChild(ctrl.cloneNode(true), ctrl);
    }

    try{
        ctrl.parentNode.querySelector("span").innerHTML = `<span>Upload File</span>`
    } catch (ex) { }
}

{/* <div class="area">
    <input type="file" class="multiple-upload" />
</div> */}