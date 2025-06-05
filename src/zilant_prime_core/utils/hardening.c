#include <seccomp.h>
#include <sys/prctl.h>

__attribute__((constructor))
void apply_runtime_hardening() {
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_ALLOW);
    if (ctx) {
        seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(ptrace), 0);
        seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(perf_event_open), 0);
        seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(process_vm_readv), 0);
        seccomp_load(ctx);
    }
    prctl(PR_SET_TIMERSLACK, 1);
    prctl(PR_SET_DUMPABLE, 0);
    prctl(PR_SET_NO_NEW_PRIVS, 1);
}
