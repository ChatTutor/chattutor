import { Component, OnInit } from '@angular/core';
import { ChatService } from 'app/chat.service';
import { Message } from 'app/models/message.model';

@Component({
  selector: 'app-message',
  templateUrl: './message.component.html',
  styleUrls: ['./message.component.css']
})
export class MessageComponent {
  sender: string;
  messageText: string;
  message: Message = {} as Message;
  constructor(public chat: ChatService, sender: string, messageText: string) {
    this.sender = sender
    this.chat = chat
    this.messageText = messageText 
  }

  async sendMessage() {
    this.message = {
      message: this.messageText,
      from: this.sender,
      date: new Date()
    }
    this.messageText = ''
    this.chat.messages.push(this.message)
    let readableStream = await this.chat.sendMessage(this.message)
    // push the new message to chat [? ]
    // this.chat.messages.push (.... readeble stream input)
    // response from chat tutor
    return readableStream
  }

}
