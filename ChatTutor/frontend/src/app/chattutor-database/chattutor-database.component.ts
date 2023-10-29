import {Component, ViewChild} from '@angular/core';
import {MatPaginator} from "@angular/material/paginator";
import {MatTableDataSource} from "@angular/material/table";
import {Message} from "../models/message.model";

@Component({
  selector: 'app-chattutor-database',
  templateUrl: './chattutor-database.component.html',
  styleUrls: ['./chattutor-database.component.css']
})
export class ChattutorDatabaseComponent {
    @ViewChild('paginator') paginator: MatPaginator;

    username: string = ''
    password: string = ''
    success_message: string = ''
    messages_in_db: any[] = []
    table_data = new MatTableDataSource<Message>(this.messages_in_db)
    columnsToDisplay = ['content', 'role'];
    async submitForm() {
        let body = JSON.stringify({lusername: this.username, lpassword: this.password})
        this.success_message = 'wait'
        let response = await fetch('/getfromdbng', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: body})
        let jsonr = await response.json()
        this.success_message = jsonr["message"]

        if (this.success_message === 'success') {
            this.messages_in_db = jsonr['messages']
            this.table_data = new MatTableDataSource<Message>(this.messages_in_db)
            this.table_data.paginator = this.paginator
        }
    }

}
