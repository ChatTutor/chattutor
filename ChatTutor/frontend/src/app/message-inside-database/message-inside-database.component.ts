import {Component, Input} from '@angular/core';
import {Message} from "../models/message.model";

@Component({
  selector: 'app-message-inside-database',
  templateUrl: './message-inside-database.component.html',
  styleUrls: ['./message-inside-database.component.css']
})
export class MessageInsideDatabaseComponent {
    @Input() message: Message | undefined = undefined

}
