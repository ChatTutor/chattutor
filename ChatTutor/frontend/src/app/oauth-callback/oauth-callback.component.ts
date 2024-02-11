import { Component, OnInit } from '@angular/core';
import { OAuthService, AuthConfig, OAuthErrorEvent } from 'angular-oauth2-oidc';
import { AuthService } from '../auth.service';



@Component({
  selector: 'app-oauth-callback',
  template: `<div>Processing login...</div>`,
  styleUrls: ['./oauth-callback.component.css']
})
export class OAuthCallbackComponent implements OnInit {
  get token() { return this.oauthService.getAccessToken(); }
  get claims() { return this.oauthService.getIdentityClaims(); }
  
  constructor(private oauthService: OAuthService, private authService: AuthService) {
    oauthService.events.subscribe(e => e instanceof OAuthErrorEvent ? console.error(e) : console.warn(e));
  }

  ngOnInit() {
    this.oauthService.loadDiscoveryDocument().then(() => {
      this.oauthService.tryLoginCodeFlow().then(() => {
        if (!this.oauthService.hasValidAccessToken()) {
          console.log('OAuth login failed or was cancelled.');
        }
        else {
          console.log('Login success!');
          this.authService.handleLoginSuccess();
        }
      })
    }).catch(err => {
      console.error('Error during login:', err);
    });
  }
}


    // this.oauthService.loadDiscoveryDocumentAndTryLogin().then(_ => {
    //   console.log(1);
      
    //   if (this.oauthService.hasValidAccessToken()) {
    //     console.log(2);
        
    //     this.authService.handleLoginSuccess();
    //     console.log(3);
        
    //   } else {
    //     // Handle login failure or redirect to a login page
    //     console.log('OAuth login failed or was cancelled.');
    //   }
    // }).catch(err => {
    //   console.error('Error during login:', err);
    // });;

