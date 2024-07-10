import {Component, OnInit, Input, EventEmitter, Output} from '@angular/core';
import {ChatService} from 'app/chat.service';
import {Message} from 'app/models/message.model';

@Component({
  selector: 'app-docheader',
  templateUrl: './docheader.component.html',
  styleUrls: ['./docheader.component.css']
})
export class DocheaderComponent implements OnInit {
  @Input() document: any = {};
  @Input() showHeader: boolean = true;
  @Output() onClose: EventEmitter<any> = new EventEmitter();
  @Output() onFocus: EventEmitter<any> = new EventEmitter();
  @Output() onClick: EventEmitter<any> = new EventEmitter();

  ngOnInit(): void { 
  }

  map_name(arr : Array<any>) {
    return arr.map(x => x['name'])
  }

  @Input() full: any = true;
  closeInfoBox() {
    this.onClose.emit()
  }
  
  focusOnDocument() {
    this.onFocus.emit(this.document)
  }

  toggleDocument() {
    this.onClick.emit()
  }
}
