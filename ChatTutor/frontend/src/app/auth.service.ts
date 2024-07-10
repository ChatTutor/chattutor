import { Injectable } from '@angular/core';
import { OAuthService, AuthConfig, OAuthErrorEvent } from 'angular-oauth2-oidc';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';


const authConfig: AuthConfig = {
  issuer: 'https://accounts.google.com',
  redirectUri: window.location.origin + '/oauth-callback',
  clientId: '731947664853-26viimvavb8qc3hmfcuah4t7f8sll2he.apps.googleusercontent.com',
  responseType: 'token id_token', // Implicit flow
  scope: 'openid profile email',
  showDebugInformation: true,
  strictDiscoveryDocumentValidation: false,
  disablePKCE: false,
};


@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(private http: HttpClient, private oauthService: OAuthService, private router: Router) {
    this.oauthService.configure(authConfig);
  }

  oauthLogin(utype: string, redirect_from: string | undefined | null): void {
    if (redirect_from === null)
      redirect_from = undefined
    console.log("Utype", utype, "red from", redirect_from);
    this.oauthService.loadDiscoveryDocument().then(() => {
      this.oauthService.initImplicitFlow(JSON.stringify({"utype" : utype, "redirect_from": redirect_from})); // For PKCE
    }).catch((err: OAuthErrorEvent) => console.error(err));
  }

  navigateToExternalUrl(url: string): void {
    window.open(url, '_blank'); // Open in a new tab/window
  }

  logout(): void {
    this.oauthService.logOut();
  }

  sendUserInfoToBackend(user_info: { google_id: string; email: string; name: string; utype: string}) {
    return this.http.post('/auth/google', user_info);    
  }

  handleLoginSuccess() {
    if (this.oauthService.hasValidAccessToken()) {
      console.log(this.oauthService.state)
      const claims: any = this.oauthService.getIdentityClaims();
      if (claims) {
        console.log("Claims: ", claims)
        // Assuming you get the google_id, email, and name from Google's OAuth response.
        const a = JSON.parse(this.oauthService.state == undefined ? "{utype: 'PROFFESSOR', 'redirect_from': undefined}" :this.oauthService.state); 
        const user_info = {
          google_id: claims.sub, // This might need adjustment based on the actual claims structure
          email: claims.email,
          name: claims.name,
          picture: claims.picture,
          utype: a['utype'],
          redirect_from: a['redirect_from']
        };
        console.log('sending to backend', user_info);
        this.sendUserInfoToBackend(user_info).subscribe(
          response =>{
              console.log('getting res...\n')
            console.log(response)
            const data = JSON.parse(JSON.stringify(response))
            if (data["redirect_to"] == undefined)
              this.router.navigate(['/']);
            else {
                console.log(data["redirect_to"] + '?chattutor_sid_' + data["sid"])
              this.navigateToExternalUrl(data["redirect_to"] + '?chattutor_sid_' + data["sid"])
              this.router.navigate(['/']);
            }
          },
          error => {
            console.error(error)
            this.router.navigate(['/']);
          }
        );
      } else {
        this.router.navigate(['/']);
      }
    }
  }

  get identityClaims(): any {
    return this.oauthService.getIdentityClaims();
  }

  get isLoggedIn(): boolean {
    return this.oauthService.hasValidAccessToken();
  }
}