// ==============================================================================
// File: apps/benchmark-runner/k6/concurrency.js
// Purpose: Many concurrent VUs, short duration — connection / pool pressure.
// SOLID: SRP — concurrency profile only. -e LANG=node
// Not executed as part of scaffolding.
// ==============================================================================

import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import { personService, protoFile, protoImportPath, resolveEndpoint } from './lib/endpoints.js';

const client = new grpc.Client();
client.load([protoImportPath], protoFile);

export const options = {
  scenarios: {
    concurrency: {
      executor: 'constant-vus',
      vus: 30,
      duration: '20s',
    },
  },
  thresholds: {
    checks: ['rate>0.85'],
  },
  tags: { test_type: 'performance', profile: 'concurrency' },
};

export default function () {
  const ep = resolveEndpoint(__ENV.LANG);
  client.connect(ep.address, { plaintext: true, timeout: '10s' });
  const res = client.invoke(`${personService}/ReadAllPersons`, { limit: 5, offset: 0 });
  check(res, { 'status OK': (r) => r && r.status === grpc.StatusOK });
  client.close();
  sleep(0.02);
}
