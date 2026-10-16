/* Build-only fixture: confirm that the pinned OLLVM plugin executes a pass
 * when cross-compiling arm64-apple-ios, not just that clang accepts a flag.
 */
__attribute__((noinline))
int dd_ollvm_probe(int input) {
    int value = input;
    for (int i = 0; i < 5; ++i) {
        value = value * 3 + i;
    }
    return value;
}
