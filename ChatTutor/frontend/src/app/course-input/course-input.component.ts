import { Component, Input } from '@angular/core';
import {MatStepperModule} from '@angular/material/stepper';
import { DataProviderService } from 'app/dataprovider.service';
import { Processes } from 'app/models/processing.model';
import { WStatus } from 'app/models/windowstatus.enum';
@Component({
  selector: 'app-course-input',
  templateUrl: './course-input.component.html',
  styleUrls: ['./course-input.component.css'],
  providers: [DataProviderService]
})
export class CourseInputComponent {
    urltoparse: string = ''
    parsed_urls_array: string[] = []
    parsed_sections: any = []//[{"section_id": "https___py_mit_edu_fall23_info_infrastructure", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/infrastructure", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_info_help", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/help", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_info_grading", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/grading", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_info_academic_integrity", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/academic_integrity", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_info_basics", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/basics", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_info_staff", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/info/staff", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_announcements", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/announcements", "course_chroma_collection": "dsamsjkldjklkallksdja"}, {"section_id": "https___py_mit_edu_fall23_calendar", "course_id": "ad4d55f0-4386-47ac-bd4a-e30e57936810", "section_url": "https://py.mit.edu/fall23/calendar", "course_chroma_collection": "dsamsjkldjklkallksdja"}]//[]
    course_name: string = ''
    proffessor: string = ''
    is_ready: boolean = false
    url_collection_name: string = ''
    urls_to_parse: string[]
    process_of: any = {}
    @Input() dashboard_only: boolean = false
    constructor(private dataProvider : DataProviderService) {
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
        
        this.parsed_sections = this.parsed_sections.filter((s:any) => {
            console.log(s['section_id'], deleted_data['deleted'])
            return s['section_id'] != deleted_data['deleted']
        })

        console.log("Removed from db")
    }

    async submitUrlToParse() {
        const urls = await this.dataProvider.addUrlsToKnowledgeBase(this.urls_to_parse, this.course_name, this.proffessor)
        console.log("Generated urls: ", urls)
        this.urls_to_parse = urls
    }

    async submitUrlScrape() {
        this.dataProvider.scrapeOriginURLNode(this.urltoparse, this.course_name, this.proffessor, this);
    }
}
