import {Component, EventEmitter, Input, Output} from '@angular/core';
import {MatChipInputEvent} from "@angular/material/chips";
import {COMMA, ENTER, SPACE} from "@angular/cdk/keycodes";

@Component({
    selector: 'app-dataset-chips',
    templateUrl: './dataset-chips.component.html',
    styleUrls: ['./dataset-chips.component.css']
})
export class DatasetChipsComponent {
    @Input() files_data: Array<File> = []
    @Input() urls_data: Array<string> = []


    @Output() added_urls_event = new EventEmitter<string>()

    protected readonly JSON = JSON;

    add(event: MatChipInputEvent): void {
        const value = (event.value || '').trim();

        // Add our fruitz
        if (value) {
            this.added_urls_event.emit(value)
        }

        // Clear the input value
        event.chipInput!.clear();
    }

    protected readonly SPACE = SPACE;
    protected readonly COMMA = COMMA;
    protected readonly ENTER = ENTER;
}
