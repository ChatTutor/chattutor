import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {Processes} from "../models/processing.model";
import { DataProviderService } from 'app/dataprovider.service';

@Component({
    selector: 'app-course-dashboard',
    templateUrl: './course-dashboard.component.html',
    styleUrls: ['./course-dashboard.component.css'],
    providers: [DataProviderService]
})
export class CourseDashboardComponent implements OnInit {
    course_id: string | null
    sections: any = []
    students: any = []
    messages: any = []
    email: string
    process_of: any = {}
    course_name: string = '[]'
    loading: boolean = true
    status: String = 'content'
    testmode: boolean = false
    runlocally: boolean = false
    tokens: any[] = []
    constructor(private route: ActivatedRoute,
        private dataProvider : DataProviderService) {
    }

    switchStatus(newstatus : String) : void {
        this.status = newstatus
    }

    ngOnInit(): void {
        this.loading = true
        console.log(this.route.snapshot.paramMap)
        this.course_id = this.route.snapshot.paramMap.get('id')
        console.log(this.course_id)

        this.dataProvider.getLoggedInUser().then(user => {
            this.email = user['email']
            this.dataProvider.getUserCourseSections(this.email, this.course_id).then(data => {
                this.sections = data["sections"]
                this.students = data["students"]
                this.messages = data["messages"]
                console.log('sections:',this.sections, "students:", this.students, "messages:", this.messages)
                this.course_name = this.sections[0]['course_chroma_collection']
                this.loading = false
            })
        })
    }


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
        this.process_of[d.doc] = Processes.Deleting
        const deleted_data = await this.dataProvider.deleteDoc_Unsafe(d.doc, d.collection)
        console.log(deleted_data['deleted'])

        this.sections = this.sections.filter((s:any) => {
            console.log(s['section_id'], deleted_data['deleted'])
            return s['section_id'] != deleted_data['deleted']
        })
        console.log("Removed from db")
    }

}
