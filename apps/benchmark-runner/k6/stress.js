// ==============================================================================
// File: apps/benchmark-runner/k6/stress.js
// Purpose: Higher-VU gRPC stress — ReadAllPersons. -e LANG=go
// SOLID: SRP — stress profile only.
// Not executed as part of scaffolding.
// ==============================================================================

import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import { defaultThresholds, personService, protoFile, protoImportPath, resolveEndpoint } from './lib/endpoints.js';

const client = new grpc.Client();
client.load([protoImportPath], protoFile);

export const options = {
  scenarios: {
    stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '20s', target: 25 },
        { duration: '40s', target: 50 },
        { duration: '20s', target: 0 },
      ],
    },
  },
  thresholds: defaultThresholds,
  tags: { test_type: 'performance', profile: 'stress' },
};

export default function () {
  const ep = resolveEndpoint(__ENV.LANG);
  client.connect(ep.address, { plaintext: true, timeout: '15s' });
  const res = client.invoke(`${personService}/ReadAllPersons`, { limit: 20, offset: 0 });
  check(res, { 'status OK': (r) => r && r.status === grpc.StatusOK });
  client.close();
  sleep(0.05);
}
