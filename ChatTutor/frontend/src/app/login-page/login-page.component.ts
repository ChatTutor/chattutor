import { Component, Input, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';
import { OAuthService, AuthConfig, OAuthErrorEvent } from 'angular-oauth2-oidc';
import { ActivatedRoute } from '@angular/router';
@Component({
  selector: 'app-login-page',
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.css']
})
export class LoginPageComponent implements OnInit{
  @Input() endpoint: String = "/login"
  @Input() stud: boolean = false
  redirect_from: string | undefined | null

  constructor(private authService: AuthService,  private oauthService: OAuthService, private route: ActivatedRoute) {
  }

  ngOnInit(): void {
    this.stud = this.route.snapshot.data['stud']
    this.redirect_from = this.route.snapshot.params['redirect_from']
    console.log(this.stud, this.redirect_from)
  }

  continueOAuth() {
    this.stud = this.route.snapshot.data['stud']
    console.log(this.stud, "stud")
    if (this.stud == true) {
      this.authService.oauthLogin("STUDENT", this.redirect_from);
    } else {
      this.authService.oauthLogin("PROFFESOR", undefined);
    }
  }
}
