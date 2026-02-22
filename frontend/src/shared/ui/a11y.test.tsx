import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { axe } from 'vitest-axe';
import 'vitest-axe/extend-expect';
import { Button } from './Button';
import { Input } from './Input';
import { Badge } from './Badge';

// Fix for vitest-axe matchers type augmentation
declare module 'vitest' {
    export interface Assertion<T = any> {
        toHaveNoViolations(): Promise<T>;
    }
}

describe('Accessibility Scans', () => {
    it('Button should have no violations', async () => {
        const { container } = render(<Button>Click Me</Button>);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });

    it('Input should have no violations with label', async () => {
        const { container } = render(<Input label="Username" id="user" />);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });

    it('Badge should have no violations', async () => {
        const { container } = render(<Badge variant="blue">Status</Badge>);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });
});
