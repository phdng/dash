; K8 isolated Kagura MVO LLVM19 IR canary.
; Real pass eligibility MUST NOT depend on Clang mem2reg/lifetime decisions.
; Only the target triple placeholder is filled in by pilot.py for the
; macOS host or iOS arm64 build. No private code, selectors or runtime hooks.
target triple = "@@TRIPLE@@"

define i64 @dd_k8_evaluate(i64 %n, i64 %salt) {
entry:
  %slot = alloca i64, align 8
  %mixed = xor i64 %n, %salt
  store volatile i64 %mixed, ptr %slot, align 8
  %value = load volatile i64, ptr %slot, align 8
  %left = shl i64 %value, 11
  %right = lshr i64 %value, 53
  %rotated = or i64 %left, %right
  %result = xor i64 %rotated, 11400714819323198485
  ret i64 %result
}
