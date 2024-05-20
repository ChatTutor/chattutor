import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NsfPaperNavComponent } from './nsf-paper-nav.component';

describe('NsfPaperNavComponent', () => {
  let component: NsfPaperNavComponent;
  let fixture: ComponentFixture<NsfPaperNavComponent>;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      declarations: [NsfPaperNavComponent]
    });
    
    fixture = TestBed.createComponent(NsfPaperNavComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
