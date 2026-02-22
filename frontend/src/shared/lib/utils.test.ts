import { describe, it, expect } from 'vitest';
import { cn } from './utils';

describe('cn utility', () => {
    it('merges tailwind classes correctly', () => {
        expect(cn('px-2', 'py-2')).toBe('px-2 py-2');
    });

    it('handles conditional classes', () => {
        expect(cn('px-2', false && 'py-2', 'bg-white')).toBe('px-2 bg-white');
    });

    it('resolves tailwind conflicts', () => {
        expect(cn('p-2', 'p-4')).toBe('p-4');
    });

    it('handles empty inputs', () => {
        expect(cn()).toBe('');
    });
});
