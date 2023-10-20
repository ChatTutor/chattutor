import { Component } from '@angular/core';
import { Paper } from 'app/models/paper.model';

@Component({
  selector: 'app-chat-window',
  templateUrl: './chat-window.component.html',
  styleUrls: ['./chat-window.component.css']
})
export class ChatWindowComponent {
  messages:any = [];
  
  onSendMessage(messageText: string) {
    this.messages.push({
      sender: 'Student',
      text: messageText,
      timestamp: new Date().toLocaleTimeString()
    });
  }

}
