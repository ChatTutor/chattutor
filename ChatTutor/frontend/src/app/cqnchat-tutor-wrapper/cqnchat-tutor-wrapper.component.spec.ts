import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CQNChatTutorWrapperComponent } from './cqnchat-tutor-wrapper.component';

describe('CQNChatTutorWrapperComponent', () => {
  let component: CQNChatTutorWrapperComponent;
  let fixture: ComponentFixture<CQNChatTutorWrapperComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CQNChatTutorWrapperComponent]
    });
    fixture = TestBed.createComponent(CQNChatTutorWrapperComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
