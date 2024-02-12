import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaperChipComponent } from './paper-chip.component';

describe('PaperChipComponent', () => {
  let component: PaperChipComponent;
  let fixture: ComponentFixture<PaperChipComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PaperChipComponent]
    });
    fixture = TestBed.createComponent(PaperChipComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
