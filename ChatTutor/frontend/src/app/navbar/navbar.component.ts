import {Component, Input, OnInit} from '@angular/core';
import { DataProviderService } from 'app/dataprovider.service';

@Component({
    selector: 'app-navbar',
    templateUrl: './navbar.component.html',
    styleUrls: ['./navbar.component.css'],
    providers: [DataProviderService]
})
export class NavbarComponent implements OnInit {
    loggedin: boolean = false
    hidden: boolean = true
    show_verif: boolean = false
    @Input() ondashboard: boolean = false
    @Input() onhomepage: boolean = false

    constructor(
        private dataProvider : DataProviderService) {
    }

    async ngOnInit(): Promise<void> {
        const user = await this.dataProvider.isAuthd();

        console.log(user['loggedin'], user)
        this.loggedin = user['loggedin']
        this.show_verif = user['loggedin'] && !(user['verified'])
        this.hidden = false
    }
}
