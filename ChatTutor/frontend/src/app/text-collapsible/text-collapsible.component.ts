import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-text-collapsible',
  templateUrl: './text-collapsible.component.html',
  styleUrls: ['./text-collapsible.component.css']
})
export class TextCollapsibleComponent {
    @Input() text: string = ''
    is_collapsed: boolean = true


    toggle_collapsed(): void {
        this.is_collapsed = !this.is_collapsed
    }
}
