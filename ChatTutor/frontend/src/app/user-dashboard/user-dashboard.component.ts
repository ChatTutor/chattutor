import {Component, Input, OnInit} from '@angular/core';

@Component({
    selector: 'app-user-dashboard',
    templateUrl: './user-dashboard.component.html',
    styleUrls: ['./user-dashboard.component.css']
})
export class UserDashboardComponent implements OnInit {
    username: string
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
        this.username = user["username"]

        const resp = await fetch(`/users/${this.username}/mycourses`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        })
        const coursess = await resp.json()
        console.log(coursess)

        this.courses = coursess["courses"]



        this.loading = false
        // fetch('/getuser', {method: 'POST', headers:{'Content-Type':'application/json'}}).then(res=>res.json())
        //   .then(user => {
        //       this.username = user['username']
        //       fetch(`/users/${this.username}/courses`, {method: 'POST', headers:{'Content-Type':'application/json'}}).then(
        //         resp => {

        //           return resp.json()
        //         }
        //       ).then(data => {
        //           this.courses = data["courses"]
        //       })
        //   })
    }
}
