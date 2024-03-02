import { Component, Input } from '@angular/core';
import { AuthService } from '../auth.service';
import { OAuthService, AuthConfig, OAuthErrorEvent } from 'angular-oauth2-oidc';
@Component({
  selector: 'app-login-page',
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.css']
})
export class LoginPageComponent {
  @Input() endpoint: String = "/login"

  constructor(private authService: AuthService, private oauthService: OAuthService) {
  }

  continueOAuth() {
    this.authService.oauthLogin();
  }
}
