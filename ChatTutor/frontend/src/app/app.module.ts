import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from 'app/app-routing.module';
import { AppComponent } from 'app/app.component';
import { MessageComponent } from 'app/message/message.component';
import { ENDPOINT_TOKEN } from './chat.service';
import { ChatWindowComponent } from './chat-window/chat-window.component';
import { InputBoxComponent } from './input-box/input-box.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent,
    MessageComponent,
    ChatWindowComponent,
    InputBoxComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule
  ],
  providers: [
    { provide: ENDPOINT_TOKEN, useValue: 'your_endpoint_url_here' },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
