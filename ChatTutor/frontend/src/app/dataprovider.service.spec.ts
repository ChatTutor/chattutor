import { TestBed } from '@angular/core/testing';

import { DataProviderService } from './dataprovider.service';

describe('DataProviderService', () => {
  let service: DataProviderService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DataProviderService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
