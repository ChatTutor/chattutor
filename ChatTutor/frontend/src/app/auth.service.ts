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

  oauthLogin(): void {
    this.oauthService.loadDiscoveryDocument().then(() => {
      this.oauthService.initImplicitFlow(); // For PKCE
    }).catch((err: OAuthErrorEvent) => console.error(err));
  }

  logout(): void {
    this.oauthService.logOut();
  }

  sendUserInfoToBackend(user_info: { google_id: string; email: string; name: string }) {
    return this.http.post('/auth/google', user_info);
  }

  handleLoginSuccess() {
    if (this.oauthService.hasValidAccessToken()) {
      const claims: any = this.oauthService.getIdentityClaims();
      if (claims) {
        // Assuming you get the google_id, email, and name from Google's OAuth response.
        const user_info = {
          google_id: claims.sub, // This might need adjustment based on the actual claims structure
          email: claims.email,
          name: claims.name,
        };
        console.log('sending to backend', user_info);
        this.sendUserInfoToBackend(user_info).subscribe(
          response => console.log(response),
          error => console.error(error)
        );
      }
      this.router.navigate(['/']);
    }
  }

  get identityClaims(): any {
    return this.oauthService.getIdentityClaims();
  }

  get isLoggedIn(): boolean {
    return this.oauthService.hasValidAccessToken();
  }
}
