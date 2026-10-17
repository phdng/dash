/* Outside the protected translation unit; deliberately never fed to Kagura opt.
 * This public fixture exercises the *build-level* allowlist boundary.
 */
#include <stdint.h>

__attribute__((noinline, used))
uint64_t dd_kagura_unprotected_sentinel(uint64_t x) {
    return (x ^ UINT64_C(0x12345678deadbeef)) +
           UINT64_C(0x9e3779b97f4a7c15);
}
