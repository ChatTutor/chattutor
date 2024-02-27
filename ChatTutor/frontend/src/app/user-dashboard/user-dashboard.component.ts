import {Component, Input, OnInit} from '@angular/core';

@Component({
    selector: 'app-user-dashboard',
    templateUrl: './user-dashboard.component.html',
    styleUrls: ['./user-dashboard.component.css']
})
export class UserDashboardComponent implements OnInit {
    email: string
    displayedColumns: string[] = ['mainpage', 'name', 'collectionname', 'professor', 'accesslink'];
    loading: boolean = true
    status: String = 'courses'

    courses: any[] = []


    switchStatus(newstatus : String) : void {
        this.status = newstatus
    }


    async ngOnInit(): Promise<void> {
        this.loading = true
        const respuser = await fetch('/getuser', {method: 'POST', headers: {'Content-Type': 'application/json'}})
        const user = await respuser.json()
        console.log(user)
        this.email = user["email"]

        const resp = await fetch(`/users/${this.email}/mycourses`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        })
        const coursess = await resp.json()
        console.log(coursess)

        this.courses = coursess["courses"]
        this.loading = false
    }
}
