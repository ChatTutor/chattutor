import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DocheaderComponent } from './docheader.component';

describe('DocheaderComponent', () => {
  let component: DocheaderComponent;
  let fixture: ComponentFixture<DocheaderComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DocheaderComponent]
    });
    fixture = TestBed.createComponent(DocheaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
