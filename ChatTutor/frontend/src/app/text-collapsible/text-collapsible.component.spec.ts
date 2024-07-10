import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TextCollapsibleComponent } from './text-collapsible.component';

describe('TextCollapsibleComponent', () => {
  let component: TextCollapsibleComponent;
  let fixture: ComponentFixture<TextCollapsibleComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TextCollapsibleComponent]
    });
    fixture = TestBed.createComponent(TextCollapsibleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
