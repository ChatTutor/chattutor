import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataProviderService } from 'app/dataprovider.service';
@Component({
  selector: 'app-nsf-paper-nav',
  templateUrl: './nsf-paper-nav.component.html',
  styleUrls: ['./nsf-paper-nav.component.css']
})
export class NsfPaperNavComponent {
  request: string
  mode: string = 'content'
  canSend: boolean = false
  data: any = []
  loading : boolean = false
  set_mode(sm : string) {
    this.mode = sm
  }

    constructor(
      private dataProvider : DataProviderService) {
  }

  async send() {
    this.loading = true
    let data = await this.dataProvider.nsfPaperRequest(this.request, this.mode)
    this.data = data
    this.loading = false
  }

  keyPressed(event: KeyboardEvent) {
      console.log(this.request)
      if ((this.request.length) > 1) {
          this.canSend = true;
      } else {
          this.canSend = false;
      }
      if (event.key === 'Enter') {
          this.send()
      }
  }
}
