import { Injectable } from '@angular/core';
import { OAuthService, AuthConfig, OAuthErrorEvent } from 'angular-oauth2-oidc';

const authConfig: AuthConfig = {
  issuer: 'https://accounts.google.com',
  redirectUri: window.location.origin,
  clientId: '731947664853-26viimvavb8qc3hmfcuah4t7f8sll2he.apps.googleusercontent.com',
  responseType: 'code', // Use 'code' for PKCE (recommended) or 'token' for implicit flow
  scope: 'openid profile email',
  showDebugInformation: true,
  strictDiscoveryDocumentValidation: false,
};

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(private oauthService: OAuthService) {
    this.oauthService.configure(authConfig);
    // this.oauthService.loadDiscoveryDocumentAndTryLogin().then(_ => {
    //   if (!this.oauthService.hasValidAccessToken()) {
    //     this.oauthService.initCodeFlow(); // For PKCE
    //     // this.oauthService.initImplicitFlow(); // For implicit flow
    //   }
    // }).catch((err: OAuthErrorEvent) => console.error(err));
  }

  oauth(): void {
    this.oauthService.loadDiscoveryDocument().then(() => {
      this.oauthService.initCodeFlow(); // For PKCE
    });
  }

  logout(): void {
    this.oauthService.logOut();
  }

  get identityClaims(): any {
    return this.oauthService.getIdentityClaims();
  }

  get isLoggedIn(): boolean {
    return this.oauthService.hasValidAccessToken();
  }
}
