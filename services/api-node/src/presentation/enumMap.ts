/**
 * @file presentation/enumMap.ts
 * @description Seed labels <-> proto enum names (keepCase proto loader).
 */

const SPECIAL: Record<string, string> = {
    FULL_TIME: 'full-time',
    PART_TIME: 'part-time',
    JOB_SEEKER: 'job seeker',
    SINGLE_PARENT: 'single parent',
    NOT_SPECIFIED: 'not specified',
    UNSPECIFIED: 'not specified'
};

export function protoEnumToSeed(enumName: string, prefix: string): string {
    let token = String(enumName || '').toUpperCase();
    if (token.startsWith(prefix)) token = token.slice(prefix.length);
    if (SPECIAL[token]) return SPECIAL[token];
    return token.toLowerCase().replace(/_/g, ' ');
}

export function seedToProtoEnum(db: string, prefix: string): string {
    const token = String(db || '').trim().toUpperCase().replace(/[\s-]+/g, '_');
    if (!token || token === 'NOT_SPECIFIED') return `${prefix}UNSPECIFIED`;
    return token.startsWith(prefix) ? token : `${prefix}${token}`;
}

export function derivedBirthDate(age: number): string {
    const year = new Date().getUTCFullYear() - Math.max(age, 0);
    return `${year}-01-01`;
}

export function clampLimit(raw: number): number {
    if (!raw || raw <= 0) return 50;
    return Math.min(raw, 500);
}

export function clampTopK(raw: number): number {
    if (!raw || raw <= 0) return 10;
    return Math.min(raw, 100);
}
