import {Component, OnInit, Input, Output, EventEmitter} from '@angular/core';
import {ChatService} from 'app/chat.service';
import {Message} from 'app/models/message.model';

@Component({
    selector: 'app-message',
    templateUrl: './message.component.html',
    styleUrls: ['./message.component.css']
})
export class MessageComponent {
    @Input() message: Message = {} as Message
    @Output() updateContextRestriction: EventEmitter<any> = new EventEmitter();
    activePaperIndex: number = 0
    constructor(public chat: ChatService) {
    }

    protected readonly JSON = JSON;
    protected readonly document = document;

    activatePaper(index: number) {
        if (this.activePaperIndex == index) {
            this.activePaperIndex = -1;
        }
        else {
            this.activePaperIndex = index
        }
    }
  
    doc_restrictContext(document: any) {
        this.updateContextRestriction.emit(document)
    }
}
