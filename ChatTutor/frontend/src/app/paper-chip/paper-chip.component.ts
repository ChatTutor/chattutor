import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-paper-chip',
  templateUrl: './paper-chip.component.html',
  styleUrls: ['./paper-chip.component.css']
})
export class PaperChipComponent {
  @Input() document: any = {}
  @Input() trigger: string = "single"
  @Input() active: boolean = false
  @Output() onRestrict: EventEmitter<any> = new EventEmitter();
  showInfo: boolean = false

  restrictContext() {
    this.onRestrict.emit(this.document)
  }

  toggleInfo() {
    this.showInfo = !this.showInfo
  }

}
