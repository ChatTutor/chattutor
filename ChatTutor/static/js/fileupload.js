const upload_files = document.querySelectorAll('.multiple-upload');

function onFile() {
    var me = this,
        file = upload.files[0],
        name = file.name.replace(/.[^/.]+$/, '');
    upload.parentNode.querySelector("span").innerHTML = name
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

{/* <div class="area">
    <input type="file" class="multiple-upload" />
</div> */}