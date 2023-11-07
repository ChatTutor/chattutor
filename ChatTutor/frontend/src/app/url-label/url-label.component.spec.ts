import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UrlLabelComponent } from './url-label.component';

describe('UrlLabelComponent', () => {
  let component: UrlLabelComponent;
  let fixture: ComponentFixture<UrlLabelComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [UrlLabelComponent]
    });
    fixture = TestBed.createComponent(UrlLabelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
