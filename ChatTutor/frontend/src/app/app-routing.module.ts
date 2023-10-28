import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {CQNChatTutorWrapperComponent} from "./cqnchat-tutor-wrapper/cqnchat-tutor-wrapper.component";
import {ChatTutorWrapperComponent} from "./chat-tutor-wrapper/chat-tutor-wrapper.component";
import { LandingPageComponent } from './landing-page/landing-page.component';

const routes: Routes = [
  {path: '', component: LandingPageComponent},
  {path: 'cqnchattutor', component: CQNChatTutorWrapperComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
