import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserMessageAnalizerComponent } from './user-message-analizer.component';

describe('UserMessageAnalizerComponent', () => {
  let component: UserMessageAnalizerComponent;
  let fixture: ComponentFixture<UserMessageAnalizerComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [UserMessageAnalizerComponent]
    });
    fixture = TestBed.createComponent(UserMessageAnalizerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
