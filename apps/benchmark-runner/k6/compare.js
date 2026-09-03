// ==============================================================================
// File: apps/benchmark-runner/k6/compare.js
// Purpose: Same ReadAllPersons payload against all six languages in one run.
//          Each VU walks LANGS in sequence; metrics are tagged with `lang`.
// SOLID: SRP — cross-language compare profile. Addressing in lib/endpoints.js.
// Dependencies: k6/net/grpc, lib/endpoints.js, shared/proto/person_service.proto
// Not executed as part of scaffolding.
// ==============================================================================

import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import {
  defaultThresholds,
  LANGS,
  personService,
  protoFile,
  protoImportPath,
  resolveEndpoint,
} from './lib/endpoints.js';

const client = new grpc.Client();
client.load([protoImportPath], protoFile);

export const options = {
  scenarios: {
    compare: {
      executor: 'constant-vus',
      vus: 3,
      duration: '30s',
    },
  },
  thresholds: defaultThresholds,
  tags: { test_type: 'performance', profile: 'compare' },
};

/**
 * Invoke ReadAllPersons once per language (one VU-worth of the LANGS walk).
 * Request + check tags carry `lang` so Grafana / summary can split series.
 */
export default function () {
  for (let i = 0; i < LANGS.length; i += 1) {
    const ep = resolveEndpoint(LANGS[i]);
    const langTags = { lang: ep.lang };
    client.connect(ep.address, { plaintext: true, timeout: '10s' });
    const res = client.invoke(
      `${personService}/ReadAllPersons`,
      { limit: 10, offset: 0 },
      { tags: langTags },
    );
    check(res, {
      'status OK': (r) => r && r.status === grpc.StatusOK,
    }, langTags);
    client.close();
  }
  sleep(0.1);
}
