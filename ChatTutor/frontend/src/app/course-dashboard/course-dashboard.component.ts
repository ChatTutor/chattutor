import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-course-dashboard',
  templateUrl: './course-dashboard.component.html',
  styleUrls: ['./course-dashboard.component.css']
})
export class CourseDashboardComponent implements OnInit {
  course_id: string | null
  sections: any = []
  username: string
  constructor(private route: ActivatedRoute) {}
  ngOnInit(): void {
    console.log(this.route.snapshot.paramMap)
    this.course_id = this.route.snapshot.paramMap.get('id')
    console.log(this.course_id)
    fetch('/getuser', {method: 'POST', headers:{'Content-Type':'application/json'}}).then(res=>res.json())
      .then(user => {
          this.username = user['username']
          fetch(`/users/${this.username}/courses/${this.course_id}`, {method: 'POST', headers:{'Content-Type':'application/json'}}).then(
            resp => resp.json()
          ).then(data => {
              this.sections = data["sections"]
          })
      })
  }


}
