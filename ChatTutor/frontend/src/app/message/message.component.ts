import {Component, OnInit, Input} from '@angular/core';
import {ChatService} from 'app/chat.service';
import {Message} from 'app/models/message.model';

@Component({
    selector: 'app-message',
    templateUrl: './message.component.html',
    styleUrls: ['./message.component.css']
})
export class MessageComponent {
    @Input() message: Message = {} as Message


    constructor(public chat: ChatService) {
    }

    protected readonly JSON = JSON;
    protected readonly document = document;
}
