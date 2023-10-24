export function JSONparse(exp, or='') {
    try {
        var a = JSON.parse(exp)
        return a;
    } catch (e) {
        return or;
    }
}