import { Component, Input } from '@angular/core';
import {MatStepperModule} from '@angular/material/stepper';
import { Processes } from 'app/models/processing.model';
import { WStatus } from 'app/models/windowstatus.enum';
@Component({
  selector: 'app-course-input',
  templateUrl: './course-input.component.html',
  styleUrls: ['./course-input.component.css']
})
export class CourseInputComponent {
    urltoparse: string = ''
    collectionname: string = ''
    parsed_urls_array: string[] = []
    parsed_sections: any = []//[{"section_id": "https___py_mit_edu_fall23_info_infrastructure", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/infrastructure", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_info_help", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/help", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_info_grading", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/grading", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_info_academic_integrity", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/academic_integrity", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_info_basics", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/basics", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_info_staff", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/staff", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_announcements", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/announcements", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_calendar", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/calendar", "course_chroma_collection": "dsamsjkldjklkallksdja"}]//[]
    course_name: string = ''
    proffessor: string = ''
    is_ready: boolean = false
    url_collection_name: string = ''
    urls_to_parse: string[]
    process_of: any = {}
    @Input() dashboard_only: boolean = false

    getStatus(doc: string) {
        if (this.process_of[doc] == null)
            return Processes.Idle
        return this.process_of[doc]
    }

    statusDel(section: any) : boolean {
        if (section == undefined)
            return true
        return this.getStatus(section['section_id']) == Processes.Deleting
    }

    async removeFromCollection(d: any) {
        let doc= d.doc
        let collection = d.collection
        let data = JSON.stringify({
            collection: collection,
            doc: doc
        })
        this.process_of[d.doc] = Processes.Deleting
        let response = await fetch('/delete_doc', {method: 'POST', headers:{'Content-Type':'application/json'}, body: data})
        const deleted_data = await response.json()

        console.log(deleted_data['deleted'])
        
        this.parsed_sections = this.parsed_sections.filter((s:any) => {
            console.log(s['section_id'], deleted_data['deleted'])
            return s['section_id'] != deleted_data['deleted']
        })

        console.log("Removed from db")
    }

    async submitUrlToParse() {
        let data = JSON.stringify({url_to_parse: this.urltoparse, collection_name: this.collectionname, coursename: this.course_name, proffessor: this.proffessor})
        let response = await fetch('/generate_bfs_array', {method: 'POST', headers:{'Content-Type':'application/json'}, body: data})
        const urls = await response.json()
        console.log("Generated urls: ", urls)
        this.urls_to_parse = urls
    }

    async submitUrlScrape() {
        let data = JSON.stringify({url_to_parse: this.urltoparse, collection_name: this.collectionname, coursename: this.course_name, proffessor: this.proffessor})
        let response = await fetch('/urlcrawler', {method: 'POST', headers:{'Content-Type':'application/json'}, body: data})
        const reader = response.body!.getReader()
        let fulldata = ''
        let added_sections : any = {}
        let course_chroma_col = ''
        async function read(element: CourseInputComponent): Promise<void> {
            let par = await reader.read()
            // return;
            if(par.done) {
                element.is_ready = true
                element.url_collection_name = course_chroma_col
                return;
            }


            const string_value = new TextDecoder().decode(par.value)
            // console.log("SVAL:",string_value)
            fulldata += ('\n\n' + string_value)
            const data:any[] = fulldata.split('\n\n')
                .filter(Boolean)
                .map(chunk => {
                    let spl = null
                    try {
                        spl = JSON.parse(chunk.split('data: ')[1]) }
                    catch (e) { spl = {}
                    }
                    return spl
                })

            console.log("DATA: ", data)
            console.log("FULL DATA: ", fulldata)
            console.log("SVA: ", string_value)



            
            data.forEach(sectionarr => {
               sectionarr.forEach((section: any) => {
                   if (added_sections[section['section_id']] != 1) {
                    element.parsed_urls_array.push(section['section_url'])
                    element.parsed_sections.push(section)
                    added_sections[section['section_id']] = 1
                    course_chroma_col = section['course_chroma_collection']
                }
               })

            })
            
            await read(element)
        }
        await read(this)
    }
}
