// ==============================================================================
// File: apps/benchmark-runner/k6/security.js
// Purpose: Safe negative payloads against THIS stack only (no exploit kits).
//          Oversized strings, SQL-looking names, huge limit / top_k.
// Expected: InvalidArgument, clamp, or empty result — never a crash / SQL exec.
// SOLID: SRP — security profile. -e LANG=csharp
// Not executed as part of scaffolding.
// ==============================================================================

import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import { personService, protoFile, protoImportPath, resolveEndpoint } from './lib/endpoints.js';

const client = new grpc.Client();
client.load([protoImportPath], protoFile);

const OVERSIZED = 'X'.repeat(20000);
const SQL_LOOKING = "Robert'); DROP TABLE persons_python;--";

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
  tags: { test_type: 'security', profile: 'security' },
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

  const hugeLimit = client.invoke(`${personService}/ReadAllPersons`, {
    limit: 999999,
    offset: 0,
  });
  check(hugeLimit, { 'huge limit handled': (r) => isSafeOutcome(r) });

  const sqlName = client.invoke(`${personService}/SearchByFilter`, {
    first_name: SQL_LOOKING,
    national_code: "1' OR '1'='1",
  });
  check(sqlName, { 'SQL-looking name handled': (r) => isSafeOutcome(r) });

  const longName = client.invoke(`${personService}/SearchByFilter`, {
    first_name: OVERSIZED,
    last_name: OVERSIZED,
  });
  check(longName, { 'oversized string handled': (r) => isSafeOutcome(r) });

  client.close();
  sleep(0.1);
}
