import {Component, Output, EventEmitter, Input} from '@angular/core';
import { WStatus } from 'app/models/windowstatus.enum';
import { OnInit, SimpleChanges, OnChanges, } from '@angular/core'

@Component({
    selector: 'app-input-box',
    templateUrl: './input-box.component.html',
    styleUrls: ['./input-box.component.css'],
})
export class InputBoxComponent implements OnChanges{
    @Output() sendMessage = new EventEmitter<string>();
    @Output() clearConvo = new EventEmitter<string>()
    @Output() stopConvo = new EventEmitter<string>()
    messageText: any = '';
    @Input() status : WStatus
    canSend: boolean = false
    canStop: boolean = true
    canClear: boolean = true

    ngOnChanges(changes: SimpleChanges) {
        console.log(changes)
        if (changes['status']) {
            console.log(changes['status'])
            if (changes['status'].currentValue == WStatus.GeneratingMessage || 
                changes['status'].currentValue == WStatus.LoadingMessage) {
                    this.canSend = false;
                    this.canStop = true;
                    this.canClear = false;
                }
        }
    }

    send() {
        this.canClear = false;
        this.sendMessage.emit(this.messageText);
        this.messageText = '';  // clear the input after sending
        setTimeout(() => {
            this.messageText = '';  // clear the input after sending
        }, 10);

    }

    keyPressed(event: KeyboardEvent) {
        console.log(this.messageText)
        if ((this.messageText.length) > 1) {
            this.canSend = true;
        } else {
            this.canSend = false;
        }
        if (event.key === 'Enter') {
            this.send()
        }
    }

    clearChat() {
        this.clearConvo.emit('');
        this.canClear = false;
    }

    stopChat() {
        this.stopConvo.emit('')
        this.canClear = true;
    }

}