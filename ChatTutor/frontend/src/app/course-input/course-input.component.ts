import { Component } from '@angular/core';

@Component({
  selector: 'app-course-input',
  templateUrl: './course-input.component.html',
  styleUrls: ['./course-input.component.css']
})
export class CourseInputComponent {
    urltoparse: string = ''
    collectionname: string = ''
    parsed_urls_array: string[] = []
    course_name: string = ''
    proffessor: string = ''
    async submitUrlScrape() {
        let data = JSON.stringify({url_to_parse: this.urltoparse, collection_name: this.collectionname, coursename: this.course_name, proffessor: this.proffessor})
        let response = await fetch('/urlcrawler', {method: 'POST', headers:{'Content-Type':'application/json'}, body: data})
        const reader = response.body!.getReader()
        async function read(element: CourseInputComponent): Promise<void> {
            let par = await reader.read()
            if(par.done) {
                return;
            }


            const string_value = new TextDecoder().decode(par.value)
                element.parsed_urls_array.push(string_value)


            await read(element)
        }
        await read(this)
    }
}
