// ==============================================================================
// File: apps/benchmark-runner/k6/load.js
// Purpose: Steady gRPC load — ReadAllPersons. Parameter: -e LANG=python
// SOLID: SRP — load profile only. Endpoints live in lib/endpoints.js.
// These scripts are scaffolding; they have not been executed in this commit.
// ==============================================================================

import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import { defaultThresholds, personService, protoFile, protoImportPath, resolveEndpoint } from './lib/endpoints.js';

const client = new grpc.Client();
client.load([protoImportPath], protoFile);

export const options = {
  scenarios: {
    load: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
    },
  },
  thresholds: defaultThresholds,
  tags: { test_type: 'performance', profile: 'load' },
};

export default function () {
  const ep = resolveEndpoint(__ENV.LANG);
  client.connect(ep.address, { plaintext: true, timeout: '10s' });
  const res = client.invoke(`${personService}/ReadAllPersons`, { limit: 10, offset: 0 });
  check(res, {
    'status OK': (r) => r && r.status === grpc.StatusOK,
  });
  client.close();
  sleep(0.1);
}
