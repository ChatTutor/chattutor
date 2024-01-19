import {Component, EventEmitter, Input, OnChanges, Output, SimpleChanges} from '@angular/core';import {MatChipInputEvent} from "@angular/material/chips";
import {COMMA, ENTER, SPACE} from "@angular/cdk/keycodes";
import { WStatus } from 'app/models/windowstatus.enum';

@Component({
    selector: 'app-dataset-chips',
    templateUrl: './dataset-chips.component.html',
    styleUrls: ['./dataset-chips.component.css']
})
export class DatasetChipsComponent implements OnChanges {
    @Input() files_data: Array<File> = []
    @Input() urls_data: Array<string> = []
    @Input() status: WStatus = WStatus.Idle
    isactive: boolean = false
    @Output() added_urls_event = new EventEmitter<string>()

    protected readonly JSON = JSON;

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['status']) {
            if (changes['status'].currentValue == WStatus.DragOver)
                this.isactive = true
        }
    }

    toggle() {
        this.isactive = !this.isactive
    }

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
    protected readonly WStatus = WStatus;

}
