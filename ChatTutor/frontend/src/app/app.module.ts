import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from 'app/app-routing.module';
import { AppComponent } from 'app/app.component';
import { MessageComponent } from 'app/message/message.component';
import { ENDPOINT_TOKEN } from './chat.service';

@NgModule({
  declarations: [
    AppComponent,
    MessageComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [
    { provide: ENDPOINT_TOKEN, useValue: 'your_endpoint_url_here' },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
