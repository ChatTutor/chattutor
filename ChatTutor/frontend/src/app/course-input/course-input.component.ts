import { Component } from '@angular/core';
import {MatStepperModule} from '@angular/material/stepper';
@Component({
  selector: 'app-course-input',
  templateUrl: './course-input.component.html',
  styleUrls: ['./course-input.component.css']
})
export class CourseInputComponent {
    urltoparse: string = ''
    collectionname: string = ''
    parsed_urls_array: string[] = []
    parsed_sections: any = []
    course_name: string = ''
    proffessor: string = ''
    is_ready: boolean = false
    url_collection_name: string = ''
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
