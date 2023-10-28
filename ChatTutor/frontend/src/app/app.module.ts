import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from 'app/app-routing.module';
import { AppComponent } from 'app/app.component';
import { MessageComponent } from 'app/message/message.component';
import { ENDPOINT_TOKEN } from './chat.service';
import { ChatWindowComponent } from './chat-window/chat-window.component';
import { InputBoxComponent } from './input-box/input-box.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

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
  ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        BrowserAnimationsModule,
        MatFormFieldModule,
        MatInputModule,
        MatIconModule,
        FormsModule,
        MatDividerModule,
        MatButtonModule,
        MatCardModule,
        MatChipsModule,
        MatTooltipModule,
        MatProgressSpinnerModule
    ],
  providers: [
    { provide: ENDPOINT_TOKEN, useValue: 'your_endpoint_url_here' },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
