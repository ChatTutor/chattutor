import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OAuthCallbackComponent } from './oauth-callback.component';

describe('OAuthCallbackComponent', () => {
  let component: OAuthCallbackComponent;
  let fixture: ComponentFixture<OAuthCallbackComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [OAuthCallbackComponent]
    });
    fixture = TestBed.createComponent(OAuthCallbackComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
