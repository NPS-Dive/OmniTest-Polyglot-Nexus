// ==============================================================================
// File: apps/benchmark-runner/k6/security.js
// Purpose: Safe negative payloads against THIS stack only (no exploit kits).
//          Oversized strings, SQL-looking names, huge limit / top_k, bad dims.
// Expected: InvalidArgument, clamp, or empty result — never a crash / SQL exec.
// SOLID: SRP — security profile. -e LANG=csharp
// Tags align with OWASP API Security Top 10:2023 (API3, API4).
// ==============================================================================

import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import { personService, protoFile, protoImportPath, resolveEndpoint } from './lib/endpoints.js';

const client = new grpc.Client();
client.load([protoImportPath], protoFile);

const OVERSIZED = 'X'.repeat(20000);
const SQL_LOOKING = "Robert'); DROP TABLE persons_python;--";
const ZERO_VEC_384 = Array(384).fill(0);

export const options = {
  scenarios: {
    security: {
      executor: 'per-vu-iterations',
      vus: 2,
      iterations: 3,
    },
  },
  thresholds: {
    // Connection must stay up. gRPC application errors are acceptable.
    checks: ['rate>0.70'],
  },
  tags: { test_type: 'security', profile: 'security', owasp: 'api3-api4' },
};

function isSafeOutcome(res) {
  if (!res) {
    return false;
  }
  // OK, InvalidArgument, OutOfRange, FailedPrecondition = handled.
  // Unavailable / Unknown after a panic is a fail.
  const okCodes = [
    grpc.StatusOK,
    grpc.StatusInvalidArgument,
    grpc.StatusOutOfRange,
    grpc.StatusFailedPrecondition,
  ];
  return okCodes.indexOf(res.status) !== -1;
}

export default function () {
  const ep = resolveEndpoint(__ENV.LANG);
  client.connect(ep.address, { plaintext: true, timeout: '15s' });

  // API4 — unrestricted resource consumption
  const hugeLimit = client.invoke(`${personService}/ReadAllPersons`, {
    limit: 999999,
    offset: 0,
  });
  check(hugeLimit, { 'api4 huge limit handled': (r) => isSafeOutcome(r) });

  const hugeTopK = client.invoke(`${personService}/SearchByVector`, {
    vector: ZERO_VEC_384,
    top_k: 999999,
  });
  check(hugeTopK, { 'api4 huge top_k handled': (r) => isSafeOutcome(r) });

  // API3 — injection / property abuse (safe strings only)
  const sqlName = client.invoke(`${personService}/SearchByFilter`, {
    first_name: SQL_LOOKING,
    national_code: "1' OR '1'='1",
  });
  check(sqlName, { 'api3 SQL-looking name handled': (r) => isSafeOutcome(r) });

  const longName = client.invoke(`${personService}/SearchByFilter`, {
    first_name: OVERSIZED,
    last_name: OVERSIZED,
  });
  check(longName, { 'api3 oversized string handled': (r) => isSafeOutcome(r) });

  // API8-adjacent — bad vector dims should not crash (verbose-error probe)
  const badDims = client.invoke(`${personService}/SearchByVector`, {
    vector: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
    top_k: 5,
  });
  check(badDims, { 'bad vector dims handled': (r) => isSafeOutcome(r) });

  client.close();
  sleep(0.1);
}
