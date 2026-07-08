# Bug report: payments pod stuck in CrashLoopBackOff after this morning's deploy

**Symptom:** After deploying the `payments` service this morning, the pod never becomes ready.
`kubectl get pods` shows it cycling:

```
NAME                        READY   STATUS             RESTARTS   AGE
payments-7d9c8b6f4-xk2lm    0/1     CrashLoopBackOff   6          8m
```

**`kubectl describe pod payments-7d9c8b6f4-xk2lm`** (trimmed):

```
Containers:
  payments:
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       Error
      Exit Code:    1
      Started:      Mon, 08 Jul 2026 09:12:03
      Finished:     Mon, 08 Jul 2026 09:12:04
    Restart Count:  6
    Limits:
      memory:  512Mi
    Liveness:   http-get http://:8080/healthz delay=10s timeout=1s period=10s #success=1 #failure=3
    Environment:
      NODE_ENV:       production
      DATABASE_URL:   <set to the key 'database-url' in secret 'payments-secrets'>  Optional: true
Events:
  Type     Reason     Age                  From     Message
  ----     ------     ----                 ----     -------
  Normal   Scheduled  8m                            Successfully assigned payments pod
  Normal   Pulled     8m (x6)                       Container image "payments:2026.07.08" already present
  Normal   Created    8m (x6)                       Created container payments
  Normal   Started    8m (x6)                       Started container payments
  Warning  BackOff    3m (x20)                       Back-off restarting failed container
```

**`kubectl logs payments-7d9c8b6f4-xk2lm --previous`:**

```
> payments@2026.07.08 start
> node dist/server.js

[boot] NODE_ENV=production
[boot] connecting to database...
Error: getaddrinfo ENOTFOUND undefined
    at GetAddrInfoReqWrap.onlookup (node:dns:...)
  config: { host: undefined, port: 5432, database: 'payments' }
[boot] fatal: could not connect to database, exiting
```

**Recent change:** this morning's PR renamed the Kubernetes Secret key from `database-url` to `db_url`
in `secret.yaml`, "to match our naming convention." The Deployment manifest was not part of that PR.

**Deployment env snippet (unchanged this morning):**

```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: payments-secrets
        key: database-url
        optional: true
```
