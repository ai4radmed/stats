type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
    level: LogLevel;
    module: string;
    message: string;
    data?: unknown;
    timestamp: string;
}

const LEVEL_PRIORITY: Record<LogLevel, number> = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3,
};

function shouldLog(level: LogLevel): boolean {
    const minLevel = (import.meta.env.PUBLIC_LOG_LEVEL || 'info') as LogLevel;
    return (LEVEL_PRIORITY[level] ?? 0) >= (LEVEL_PRIORITY[minLevel] ?? 1);
}

function createLog(level: LogLevel, module: string, message: string, data?: unknown): LogEntry {
    return {
        level,
        module,
        message,
        data,
        timestamp: new Date().toISOString(),
    };
}

export function createLogger(module: string) {
    return {
        debug: (message: string, data?: unknown) => {
            if (!shouldLog('debug')) return;
            const entry = createLog('debug', module, message, data);
            console.debug(JSON.stringify(entry));
        },
        info: (message: string, data?: unknown) => {
            if (!shouldLog('info')) return;
            const entry = createLog('info', module, message, data);
            console.log(JSON.stringify(entry));
        },
        warn: (message: string, data?: unknown) => {
            if (!shouldLog('warn')) return;
            const entry = createLog('warn', module, message, data);
            console.warn(JSON.stringify(entry));
        },
        error: (message: string, data?: unknown) => {
            if (!shouldLog('error')) return;
            const entry = createLog('error', module, message, data);
            console.error(JSON.stringify(entry));
        },
    };
}
