import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MessageInsideDatabaseComponent } from './message-inside-database.component';

describe('MessageInsideDatabaseComponent', () => {
  let component: MessageInsideDatabaseComponent;
  let fixture: ComponentFixture<MessageInsideDatabaseComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MessageInsideDatabaseComponent]
    });
    fixture = TestBed.createComponent(MessageInsideDatabaseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
