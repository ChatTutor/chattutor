import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DataProviderService } from 'app/dataprovider.service';

@Component({
  selector: 'app-user-message-analizer',
  templateUrl: './user-message-analizer.component.html',
  styleUrls: ['./user-message-analizer.component.css']
})
export class UserMessageAnalizerComponent implements OnInit{
  loading: boolean = true
  course_id: string | null
  email: string
  messages: any = []
  uid: string | null
  empty = false

  constructor(private route: ActivatedRoute,
      private dataProvider : DataProviderService) {
  }

  ngOnInit(): void {
    this.loading = true
    console.log(this.route.snapshot.paramMap)
    this.course_id = this.route.snapshot.paramMap.get('id')
    this.uid = this.route.snapshot.paramMap.get('uid')
    console.log(this.course_id)

    this.dataProvider.getLoggedInUser().then(user => {
        this.email = user['email']
        this.dataProvider.getCourseMessagesByUID(this.email, this.course_id, this.uid).then(data => {
            this.messages = data["messages"]
            this.loading = false
            this.empty = (this.messages.length == 0)
        })
    })
}

}
