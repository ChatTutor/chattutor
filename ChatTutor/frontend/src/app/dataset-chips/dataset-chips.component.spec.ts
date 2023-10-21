import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DatasetChipsComponent } from './dataset-chips.component';

describe('DatasetChipsComponent', () => {
  let component: DatasetChipsComponent;
  let fixture: ComponentFixture<DatasetChipsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DatasetChipsComponent]
    });
    fixture = TestBed.createComponent(DatasetChipsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
