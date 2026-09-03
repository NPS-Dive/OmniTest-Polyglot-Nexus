// ==============================================================================
// File: apps/benchmark-runner/k6/scalability.js
// Purpose: Capacity curve — ramping VUs 0 → 5 → 10 → 20 → 0, ReadAllPersons.
// SOLID: SRP — scalability profile only. Addressing in lib/endpoints.js.
// Dependencies: k6/net/grpc, lib/endpoints.js, shared/proto/person_service.proto
// Not executed as part of scaffolding.
// ==============================================================================

import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import { defaultThresholds, personService, protoFile, protoImportPath, resolveEndpoint } from './lib/endpoints.js';

const client = new grpc.Client();
client.load([protoImportPath], protoFile);

export const options = {
  scenarios: {
    scalability: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '20s', target: 5 },
        { duration: '20s', target: 10 },
        { duration: '20s', target: 20 },
        { duration: '20s', target: 0 },
      ],
    },
  },
  thresholds: defaultThresholds,
  tags: { test_type: 'performance', profile: 'scalability' },
};

/**
 * One scalability iteration: ReadAllPersons against LANG (default go).
 */
export default function () {
  const ep = resolveEndpoint(__ENV.LANG);
  client.connect(ep.address, { plaintext: true, timeout: '15s' });
  const res = client.invoke(
    `${personService}/ReadAllPersons`,
    { limit: 10, offset: 0 },
    { tags: { lang: ep.lang } },
  );
  check(res, {
    'status OK': (r) => r && r.status === grpc.StatusOK,
  }, { lang: ep.lang });
  client.close();
  sleep(0.05);
}
