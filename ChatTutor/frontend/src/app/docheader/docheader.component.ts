import {Component, OnInit, Input, EventEmitter, Output} from '@angular/core';
import {ChatService} from 'app/chat.service';
import {Message} from 'app/models/message.model';

@Component({
  selector: 'app-docheader',
  templateUrl: './docheader.component.html',
  styleUrls: ['./docheader.component.css']
})
export class DocheaderComponent {
  @Input() document: any = {};
  @Input() showHeader: boolean = true;
  @Output() onClose: EventEmitter<any> = new EventEmitter();
  @Output() onFocus: EventEmitter<any> = new EventEmitter();
  closeInfoBox() {
    this.onClose.emit()
  }
  
  focusOnDocument() {
    this.onFocus.emit(this.document)
  }
}
