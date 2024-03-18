import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';

@Component({
    selector: 'app-url-label',
    templateUrl: './url-label.component.html',
    styleUrls: ['./url-label.component.css']
})
export class UrlLabelComponent implements OnInit {
    @Input() url_name: string = ''
    @Input() section_info: any = []
    @Output() onRemove: EventEmitter<any> = new EventEmitter()
    @Input() isDeleting: boolean = false
    from_doc_joined = this.section_info['pullingfrom'] != null ? this.section_info['pullingfrom'] : this.section_info['section_id']
    toggle_input = false
    url_to_add = ''
    files_to_add: FileList | null = null

    ngOnInit(): void {
        this.from_doc_joined = this.section_info['pullingfrom'] != null ? this.section_info['pullingfrom'] : this.section_info['section_id']
    }

    emitRemove(doc: string, collection: string) {
        this.onRemove.emit({
            doc: doc,
            collection: collection
        })
    }

    toggleInputBox() {
        this.toggle_input = !this.toggle_input
    }

    onFileChanged(event: Event) {

        let target = (event.target as HTMLInputElement);
        if (target == null) {
            console.log("Encountered error!")
            return
        }
        this.files_to_add = target!.files;
    }

    async addFileToSection() {
        console.log("Add files! ", this.files_to_add)
        // interface

        let name = this.section_info['course_chroma_collection']

        const formdata = new FormData();

        formdata.append('collection_name', name)

        for (let id = 0; id < this.files_to_add!.length; id += 1) {
            let file = this.files_to_add!.item(id);
            if (file != null) {
                formdata.append('file', file, file.name)
            }
        }
        let fv = "";
        for (let id = 0; id < this.files_to_add!.length; id += 1) {
            let file = this.files_to_add!.item(id);
            fv = fv + file!.name + "$";
        }



        const res = await fetch('/upload_data_from_drop', {
            method: 'POST',
            headers: {'Accept': 'multipart/form-data'},
            body: formdata
        })

        const message = await res.json();

        console.log(message)

        const just_added = fv.substring(0, fv.length - 2)

        this.from_doc_joined = this.from_doc_joined + "$" + just_added


        let data = JSON.stringify({
            collection: this.section_info['course_chroma_collection'],
            section_id: this.section_info['section_id'],
            url_to_add: just_added
        })

        let response2 = await fetch('/add_doc_tosection', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: data
        })

        this.files_to_add = null;
    }

    getFromDocs() {
        return this.from_doc_joined.split("$")
    }

    async addURLToSection() {
        console.log("Try to add:", this.url_to_add)
        if (this.url_to_add.length < 1) {
            return
        }

        let add_to_chroma_db_args = JSON.stringify({
            name: this.section_info['course_chroma_collection'],
            url: [this.url_to_add]
        })

        let response = await fetch('/upload_site_url', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: add_to_chroma_db_args
        })
        const r = await response.json()

        console.log("Responding:", r)
        var just_added = r["docs"][0]

        if (just_added.includes("/_already_exists")) {
            just_added = just_added.split("/")[0]
            console.log(just_added + " ommited as already exists!")
        }
        console.log("adding to section db")

        let data = JSON.stringify({
            collection: this.section_info['course_chroma_collection'],
            section_id: this.section_info['section_id'],
            url_to_add: just_added
        })

        let response2 = await fetch('/add_doc_tosection', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: data
        })

        const r2 = await response2.json()

        this.from_doc_joined = this.from_doc_joined + "$" + just_added
        console.log(this.from_doc_joined)
    }
}
