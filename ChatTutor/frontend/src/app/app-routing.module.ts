import {NgModule} from '@angular/core';
import {RouterModule, Routes, UrlSegment} from '@angular/router';
import {CQNChatTutorWrapperComponent} from "./cqnchat-tutor-wrapper/cqnchat-tutor-wrapper.component";
import {ChatTutorWrapperComponent} from "./chat-tutor-wrapper/chat-tutor-wrapper.component";
import {LandingPageComponent} from './landing-page/landing-page.component';
import {CourseInputComponent} from "./course-input/course-input.component";
import {UserDashboardComponent} from './user-dashboard/user-dashboard.component';
import {CourseDashboardComponent} from './course-dashboard/course-dashboard.component';
import {LoginPageComponent} from './login-page/login-page.component';
import {RegisterPageComponent} from './register-page/register-page.component';
import {RegisterStudentPageComponent} from './register-student-page/register-student-page.component';
import {OAuthCallbackComponent} from './oauth-callback/oauth-callback.component';
import {UserPasswordResetComponent} from "./user-password-reset/user-password-reset.component";
import { OauthCallbackStudentsComponent } from './oauth-callback-students/oauth-callback-students.component';
import { UserMessageAnalizerComponent } from './user-message-analizer/user-message-analizer.component';

const routes: Routes = [
    {path: '', component: LandingPageComponent},
    {path: 'chatcqn', component: CQNChatTutorWrapperComponent},
    {path: 'chattutor', component: ChatTutorWrapperComponent},
    {path: 'scrape', component: CourseInputComponent},
    {path: 'mycourses', component: UserDashboardComponent},
    {path: 'courses/:id', component: CourseDashboardComponent},
    {path: 'courses/:id/messages/:uid', component: UserMessageAnalizerComponent},
    {path: 'login', component: LoginPageComponent, data: {stud: false}},
    {path: 'student/login', component: LoginPageComponent, data: {stud: true}},
    {path: 'student/login/:redirect_from', component: LoginPageComponent, data: {stud: true}},
    {path: 'register', component: RegisterPageComponent},
    {path: 'student/register', component: RegisterStudentPageComponent},
    {path: 'oauth-callback', component: OAuthCallbackComponent},
    {path: 'users/resetpassword', component: UserPasswordResetComponent}
];


@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule {
}
