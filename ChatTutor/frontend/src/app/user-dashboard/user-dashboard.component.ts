import {Component, Input, OnInit} from '@angular/core';
import { DataProviderService } from 'app/dataprovider.service';

@Component({
    selector: 'app-user-dashboard',
    templateUrl: './user-dashboard.component.html',
    styleUrls: ['./user-dashboard.component.css'],
    providers: [DataProviderService]
})
export class UserDashboardComponent implements OnInit {
    email: string
    displayedColumns: string[] = ['mainpage', 'name', 'collectionname', 'professor', 'accesslink'];
    loading: boolean = true
    status: String = 'courses'

    courses: any[] = []
    constructor(private dataProvider : DataProviderService) {
    }

    switchStatus(newstatus : String) : void {
        this.status = newstatus
    }


    async ngOnInit(): Promise<void> {
        this.loading = true
        const user = await this.dataProvider.getLoggedInUser();
        console.log(user)
        this.email = user["email"]

        const coursess = await this.dataProvider.getUserCourses(this.email);
        console.log(coursess)

        this.courses = coursess["courses"]
        this.loading = false
    }
}
