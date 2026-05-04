
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function debounce<T extends (...args: any[]) => void>(
    func: T,
    wait: number
): (...args: Parameters<T>) => void {
    let timeout: ReturnType<typeof setTimeout> | undefined;

    return function(this: ThisParameterType<T>, ...args: Parameters<T>): void {
        // eslint-disable-next-line @typescript-eslint/no-this-alias
        const context = this;
        const later = function() {
            timeout = undefined;
            func.apply(context, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
