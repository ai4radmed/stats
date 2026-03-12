// Mock for astro:actions module in Vitest
// Provides stub implementations for server action utilities

export function defineAction(config: any) {
    return config.handler;
}

export const ActionError = class ActionError extends Error {
    code: string;
    constructor({ code, message }: { code: string; message: string }) {
        super(message);
        this.code = code;
        this.name = 'ActionError';
    }
};
