import { Component, Input } from '@angular/core';
import { AuthService } from '../auth.service'; // Adjust the path as necessary

@Component({
  selector: 'app-login-page',
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.css']
})
export class LoginPageComponent {
  @Input() endpoint: String = "/login"
  constructor(private authService: AuthService) { }

  oauth() {
    this.authService.oauth();
  }
}
