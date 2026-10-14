# SecureSoft TrustTunnelClient build rule

The owner confirmed on 2026-10-14 that SecureSoft native libraries and client
artifacts are built on the local workstation. Do not dispatch GitHub Actions,
hosted runners, ARC runners, or other remote builders unless the owner
explicitly requests a remote build for that task. Existing CI results may be
read as evidence. Set up missing tools locally or record the exact blocker;
do not substitute a remote build on your own.

Keep experimental outputs out of published packages and customer releases.
Record source commit, build command, ABI, SHA-256 and integration validation
for every library copied into the client.
