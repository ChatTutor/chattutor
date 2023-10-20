import { Component, Output, EventEmitter } from '@angular/core';


@Component({
  selector: 'app-input-box',
  templateUrl: './input-box.component.html',
  styleUrls: ['./input-box.component.css'],
})
export class InputBoxComponent {
  @Output() sendMessage = new EventEmitter<string>();
  messageText:any = '';

  send() {
    this.sendMessage.emit(this.messageText);
    this.messageText = '';  // clear the input after sending
  }

  keyPressed(event: KeyboardEvent) {
      if (event.key === 'Enter') {
          this.send()
      }
  }



}
