import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserPasswordResetComponent } from './user-password-reset.component';

describe('UserPasswordResetComponent', () => {
  let component: UserPasswordResetComponent;
  let fixture: ComponentFixture<UserPasswordResetComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [UserPasswordResetComponent]
    });
    fixture = TestBed.createComponent(UserPasswordResetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
