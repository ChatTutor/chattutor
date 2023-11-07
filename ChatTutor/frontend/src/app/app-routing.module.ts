import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {CQNChatTutorWrapperComponent} from "./cqnchat-tutor-wrapper/cqnchat-tutor-wrapper.component";
import {ChatTutorWrapperComponent} from "./chat-tutor-wrapper/chat-tutor-wrapper.component";
import { LandingPageComponent } from './landing-page/landing-page.component';
import {ChattutorDatabaseComponent} from "./chattutor-database/chattutor-database.component";
import {CourseInputComponent} from "./course-input/course-input.component";

const routes: Routes = [
  {path: '', component: LandingPageComponent},
  {path: 'cqnchattutor', component: CQNChatTutorWrapperComponent},
    {path: 'chattutordatabase', component: ChattutorDatabaseComponent},
    {path: 'chattutord', component: ChatTutorWrapperComponent},
    {path: 'scrape', component: CourseInputComponent}
];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
