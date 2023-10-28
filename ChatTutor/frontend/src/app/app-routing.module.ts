import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {CQNChatTutorWrapperComponent} from "./cqnchat-tutor-wrapper/cqnchat-tutor-wrapper.component";
import {ChatTutorWrapperComponent} from "./chat-tutor-wrapper/chat-tutor-wrapper.component";

const routes: Routes = [{path: 'cqnchattutor', component: CQNChatTutorWrapperComponent}];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
