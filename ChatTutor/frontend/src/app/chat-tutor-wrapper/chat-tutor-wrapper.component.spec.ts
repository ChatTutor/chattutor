import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatTutorWrapperComponent } from './chat-tutor-wrapper.component';

describe('ChatTutorWrapperComponent', () => {
  let component: ChatTutorWrapperComponent;
  let fixture: ComponentFixture<ChatTutorWrapperComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ChatTutorWrapperComponent]
    });
    fixture = TestBed.createComponent(ChatTutorWrapperComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
