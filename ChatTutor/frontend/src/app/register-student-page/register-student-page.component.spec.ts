import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RegisterStudentPageComponent } from './register-student-page.component';

describe('RegisterStudentPageComponent', () => {
  let component: RegisterStudentPageComponent;
  let fixture: ComponentFixture<RegisterStudentPageComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [RegisterStudentPageComponent]
    });
    fixture = TestBed.createComponent(RegisterStudentPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
