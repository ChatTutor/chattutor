import { Component, OnInit, Input } from '@angular/core';
import { ChatService } from 'app/chat.service';
import { Message } from 'app/models/message.model';

@Component({
  selector: 'app-message',
  templateUrl: './message.component.html',
  styleUrls: ['./message.component.css']
})
export class MessageComponent {
  @Input() sender: string='';
  @Input() text: string='';
  @Input() timestamp: string='';

  message: Message = {} as Message;

  constructor(public chat: ChatService) {}

  async sendMessage() {
    this.message = {
      message: this.text,
      from: this.sender,
      date: new Date()
    };
    this.text = '';
    this.chat.messages.push(this.message);
    let readableStream = await this.chat.sendMessage(this.message);
    // push the new message to chat [? ]
    // this.chat.messages.push (.... readeble stream input)
    // response from chat tutor
    return readableStream;
  }
}
