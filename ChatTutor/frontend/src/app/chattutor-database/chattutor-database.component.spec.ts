import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChattutorDatabaseComponent } from './chattutor-database.component';

describe('ChattutorDatabaseComponent', () => {
  let component: ChattutorDatabaseComponent;
  let fixture: ComponentFixture<ChattutorDatabaseComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ChattutorDatabaseComponent]
    });
    fixture = TestBed.createComponent(ChattutorDatabaseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
