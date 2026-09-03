// ==============================================================================
// File: apps/benchmark-runner/k6/endurance.js
// Purpose: Soak / endurance gRPC load — constant 5 VUs for 2m, ReadAllPersons.
// SOLID: SRP — endurance (soak) profile only. Addressing in lib/endpoints.js.
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
    endurance: {
      executor: 'constant-vus',
      vus: 5,
      duration: '2m',
    },
  },
  thresholds: defaultThresholds,
  tags: { test_type: 'performance', profile: 'endurance' },
};

/**
 * One soak iteration: ReadAllPersons limit 10 against LANG (default go).
 */
export default function () {
  const ep = resolveEndpoint(__ENV.LANG);
  client.connect(ep.address, { plaintext: true, timeout: '10s' });
  const res = client.invoke(
    `${personService}/ReadAllPersons`,
    { limit: 10, offset: 0 },
    { tags: { lang: ep.lang } },
  );
  check(res, {
    'status OK': (r) => r && r.status === grpc.StatusOK,
  }, { lang: ep.lang });
  client.close();
  sleep(0.1);
}
