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
    async submitUrlScrape() {
        let data = JSON.stringify({url_to_parse: this.urltoparse, collection_name: this.collectionname, coursename: this.course_name, proffessor: this.proffessor})
        let response = await fetch('/urlcrawler', {method: 'POST', headers:{'Content-Type':'application/json'}, body: data})
        const reader = response.body!.getReader()
        let fulldata = ''
        let added_sections : any = {}
        async function read(element: CourseInputComponent): Promise<void> {
            let par = await reader.read()
            if(par.done) {
                element.is_ready = true
                return;
            }


            const string_value = new TextDecoder().decode(par.value)
            console.log(string_value)
            fulldata += string_value
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
            
            data.forEach(section => {
                if (added_sections[section['section_id']] != 1) {
                    element.parsed_urls_array.push(section['section_url'])
                    element.parsed_sections.push(section)
                    added_sections[section['section_id']] = 1
                }
            })
            
            await read(element)
        }
        await read(this)
    }
}
