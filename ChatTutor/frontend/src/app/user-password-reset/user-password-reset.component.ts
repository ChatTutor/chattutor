import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-user-password-reset',
  templateUrl: './user-password-reset.component.html',
  styleUrls: ['./user-password-reset.component.css']
})
export class UserPasswordResetComponent {
    @Input() checkresetcode: String = "/users/forgotpassword"
    @Input() sendresetemail: String = "/users/sendresetemail"
}
