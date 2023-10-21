import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-dataset-chips',
  templateUrl: './dataset-chips.component.html',
  styleUrls: ['./dataset-chips.component.css']
})
export class DatasetChipsComponent {
    @Input() files_data: Array<File> = []
    @Input() urls_data: Array<string> = []

    protected readonly JSON = JSON;
}
