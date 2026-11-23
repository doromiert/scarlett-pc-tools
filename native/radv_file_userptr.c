// SPDX-License-Identifier: GPL-3.0-or-later
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <stdio.h>
#include <stdatomic.h>
#include <pthread.h>
#include <xf86drm.h>
#include <amdgpu_drm.h>

// libdrm's default ANONONLY request rejects Wine's pagefile-backed shared views.
// Retry that one refusal without the optional flag; the kernel still validates
// and registers the complete range. This changes only the process loading us.
typedef int (*DrmCall)(int, unsigned long, void *, unsigned long);
static DrmCall original;
static pthread_once_t resolve_once = PTHREAD_ONCE_INIT;
static void resolve_original(void) {
    original = (DrmCall)dlsym(RTLD_NEXT, "drmCommandWriteRead");
    if (!original) {
        // Wine loads the driver locally; its libdrm may be outside RTLD_NEXT's scope.
        void *lib = dlopen("libdrm.so.2", RTLD_LAZY | RTLD_LOCAL);
        if (lib) original = (DrmCall)dlsym(lib, "drmCommandWriteRead");
    }
    if (!original) fprintf(stderr, "[scarlett] cannot resolve libdrm: %s\n", dlerror());
}

int drmCommandWriteRead(int fd, unsigned long command, void *data, unsigned long size) {
    pthread_once(&resolve_once, resolve_original);
    if (!original) return -ENOSYS;
    int result = original(fd, command, data, size);
    if (result == -EPERM && command == DRM_AMDGPU_GEM_USERPTR &&
        data && size == sizeof(struct drm_amdgpu_gem_userptr)) {
        struct drm_amdgpu_gem_userptr *request = data;
        unsigned flags = request->flags;
        if (flags & AMDGPU_GEM_USERPTR_ANONONLY) {
            request->flags &= ~AMDGPU_GEM_USERPTR_ANONONLY;
            result = original(fd, command, data, size);
            request->flags = flags;
            static _Atomic unsigned count;
            if (atomic_fetch_add(&count, 1) < 4)
                fprintf(stderr, "[scarlett] shared userptr retry: bytes=%llu result=%d\n",
                        (unsigned long long)request->size, result);
        }
    }
    return result;
}
