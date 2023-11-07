import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-url-label',
  templateUrl: './url-label.component.html',
  styleUrls: ['./url-label.component.css']
})
export class UrlLabelComponent {
    @Input() url_name: string = ''

}
