// ==============================================================================
// File: apps/benchmark-runner/k6/spike.js
// Purpose: Sudden VU spike then drop. -e LANG=java
// SOLID: SRP — spike profile only.
// Not executed as part of scaffolding.
// ==============================================================================

import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import { personService, protoFile, protoImportPath, resolveEndpoint } from './lib/endpoints.js';

const client = new grpc.Client();
client.load([protoImportPath], protoFile);

export const options = {
  scenarios: {
    spike: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '10s', target: 1 },
        { duration: '5s', target: 40 },
        { duration: '15s', target: 40 },
        { duration: '5s', target: 1 },
        { duration: '10s', target: 1 },
      ],
    },
  },
  thresholds: {
    checks: ['rate>0.80'],
  },
  tags: { test_type: 'performance', profile: 'spike' },
};

export default function () {
  const ep = resolveEndpoint(__ENV.LANG);
  client.connect(ep.address, { plaintext: true, timeout: '15s' });
  const res = client.invoke(`${personService}/SearchByFilter`, { first_name: 'A' });
  check(res, { 'status OK': (r) => r && r.status === grpc.StatusOK });
  client.close();
  sleep(0.05);
}
