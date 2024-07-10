import { Component } from '@angular/core';
import { OAuthService, AuthConfig, OAuthErrorEvent } from 'angular-oauth2-oidc';
import { AuthService } from 'app/auth.service';
@Component({
  selector: 'app-oauth-callback-students',
  templateUrl: './oauth-callback-students.component.html',
  styleUrls: ['./oauth-callback-students.component.css']
})
export class OauthCallbackStudentsComponent {
  get token() { return this.oauthService.getAccessToken(); }
  get claims() { return this.oauthService.getIdentityClaims(); }

  constructor(private oauthService: OAuthService, private authService: AuthService) {
    oauthService.events.subscribe((e: any) => e instanceof OAuthErrorEvent ? console.error(e) : console.warn(e));
  }

  ngOnInit() {
    this.oauthService.loadDiscoveryDocument().then(() => {
      this.oauthService.tryLoginImplicitFlow().then(() => {
        if (!this.oauthService.hasValidAccessToken()) {
          console.log('OAuth login failed or was cancelled.');
        }
        else {
          console.log('Student login success!');
          this.authService.handleLoginSuccess();
        }
      })
    }).catch(err => {
      console.error('Error during login:', err);
    });
  }
}
