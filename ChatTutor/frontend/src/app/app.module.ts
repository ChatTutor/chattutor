import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from 'app/app-routing.module';
import { AppComponent } from 'app/app.component';
import { MessageComponent } from 'app/message/message.component';
import { ENDPOINT_TOKEN } from './chat.service';
import { ChatWindowComponent } from './chat-window/chat-window.component';
import { InputBoxComponent } from './input-box/input-box.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatListModule } from '@angular/material/list';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import {MatDividerModule} from '@angular/material/divider';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from "@angular/material/card";
import { DatasetChipsComponent } from './dataset-chips/dataset-chips.component';
import {MatChipsModule} from "@angular/material/chips";
import { DocheaderComponent } from './docheader/docheader.component';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { PaperChipComponent } from './paper-chip/paper-chip.component';
import { ChatTutorWrapperComponent } from './chat-tutor-wrapper/chat-tutor-wrapper.component';
import { CQNChatTutorWrapperComponent } from './cqnchat-tutor-wrapper/cqnchat-tutor-wrapper.component';
import {HashLocationStrategy, LocationStrategy, PathLocationStrategy} from "@angular/common";
import { LandingPageComponent } from './landing-page/landing-page.component';
import { MessageInsideDatabaseComponent } from './message-inside-database/message-inside-database.component';
import {MatTableModule} from "@angular/material/table";
import {MatPaginatorModule} from "@angular/material/paginator";
import { CourseInputComponent } from './course-input/course-input.component';
import { UrlLabelComponent } from './url-label/url-label.component';
import {MatStepperModule} from '@angular/material/stepper';
import {MatExpansionModule} from '@angular/material/expansion';
import { UserDashboardComponent } from './user-dashboard/user-dashboard.component';
import { CourseDashboardComponent } from './course-dashboard/course-dashboard.component';
import { NavbarComponent } from './navbar/navbar.component';
import { MathjaxComponent } from './mathjax/mathjax.component';
import { LoginPageComponent } from './login-page/login-page.component';
import { RegisterPageComponent } from './register-page/register-page.component';
import { RegisterStudentPageComponent } from './register-student-page/register-student-page.component';
import { GradientBackgroundComponent } from './gradient-background/gradient-background.component';
import { OAuthCallbackComponent } from './oauth-callback/oauth-callback.component';
import {MatCheckboxModule} from '@angular/material/checkbox';


import { OAuthModule, AuthConfig, JwksValidationHandler, ValidationHandler, OAuthStorage, OAuthModuleConfig } from 'angular-oauth2-oidc'; // Added
import { AuthService } from './auth.service';
import { HttpClientModule } from '@angular/common/http';
import { UserPasswordResetComponent } from './user-password-reset/user-password-reset.component';
import { OauthCallbackStudentsComponent } from './oauth-callback-students/oauth-callback-students.component';
import { UserMessageAnalizerComponent } from './user-message-analizer/user-message-analizer.component';

const authModuleConfig: OAuthModuleConfig = {
  resourceServer: {
    allowedUrls: ['http://localhost:5000/', 'https://beta-chattutor-nbqjgewnea-uc.a.run.app/', 'https://chattutor.org/'],
    sendAccessToken: true,
  },
};

@NgModule({
  declarations: [
    AppComponent,
    MessageComponent,
    ChatWindowComponent,
    InputBoxComponent,
    DatasetChipsComponent,
    DocheaderComponent,
    PaperChipComponent,
    ChatTutorWrapperComponent,
    CQNChatTutorWrapperComponent,
    LandingPageComponent,
    MessageInsideDatabaseComponent,
    MathjaxComponent,
    CourseInputComponent,
    UrlLabelComponent,
    UserDashboardComponent,
    CourseDashboardComponent,
    NavbarComponent,
    MathjaxComponent,
    LoginPageComponent,
    RegisterPageComponent,
    RegisterStudentPageComponent,
    GradientBackgroundComponent,
    OAuthCallbackComponent,
    UserPasswordResetComponent,
    OauthCallbackStudentsComponent,
    UserMessageAnalizerComponent,
  ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        BrowserAnimationsModule,
        MatFormFieldModule,
        MatInputModule,
        MatIconModule,
        MatListModule,
        FormsModule,
        MatDividerModule,
        MatButtonModule,
        MatCardModule,
        MatChipsModule,
        MatTooltipModule,
        MatProgressSpinnerModule,
        MatTableModule,
        MatPaginatorModule,
        MatStepperModule,
        MatExpansionModule,
        HttpClientModule,
        MatCheckboxModule,
        OAuthModule.forRoot(authModuleConfig),
    ],
  providers: [
    { provide: ENDPOINT_TOKEN, useValue: 'your_endpoint_url_here' },
    { provide: OAuthModuleConfig, useValue: authModuleConfig },
    { provide: OAuthStorage, useValue: localStorage },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
