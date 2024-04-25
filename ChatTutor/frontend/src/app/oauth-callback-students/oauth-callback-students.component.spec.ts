import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OauthCallbackStudentsComponent } from './oauth-callback-students.component';

describe('OauthCallbackStudentsComponent', () => {
  let component: OauthCallbackStudentsComponent;
  let fixture: ComponentFixture<OauthCallbackStudentsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [OauthCallbackStudentsComponent]
    });
    fixture = TestBed.createComponent(OauthCallbackStudentsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
