# Cloud & IaC Security (Phase 8)

Read this for Terraform/CloudFormation/Pulumi/ARM/Bicep or direct AWS/Azure/GCP review. IaC is high-leverage: one misconfigured resource block provisions an internet-open datastore across every environment. Audit the declared state; where you have cloud MCP/CLI access, verify the live state too.

## The recurring cloud mistakes (check these first)

- **Public data storage:** S3 buckets with public ACLs / `block_public_access` disabled / policy allowing `*` principal; GCS `allUsers`/`allAuthenticatedUsers`; Azure Blob container public access; public RDS/Redshift/Cosmos/Cloud SQL. A public bucket with customer data is CRITICAL — this is the single most common cloud breach.
- **Open security groups / firewall rules:** ingress `0.0.0.0/0` to sensitive ports — 22 (SSH), 3389 (RDP), 3306/5432/1433/27017/6379 (databases), or all ports. Management and database ports open to the internet are HIGH–CRITICAL.
- **Over-permissive IAM:** policies with `"Action": "*"` and `"Resource": "*"`, `iam:PassRole` with wildcards, `AdministratorAccess` on roles/users/service accounts that don't need it, `*` principal in a resource/trust policy (confused-deputy, cross-account escalation), GCP `roles/owner|editor` on service accounts, Azure `Owner`/`Contributor` at subscription scope. Least privilege is the entire game here.
- **Unencrypted at rest / in transit:** storage, volumes (EBS), databases, snapshots, and queues without encryption; load balancers/listeners allowing plaintext HTTP; TLS not enforced.
- **Missing logging & monitoring:** CloudTrail/Config/GuardDuty (AWS), Cloud Audit Logs/SCC (GCP), Activity Log/Defender (Azure) disabled; VPC/flow logs off; log buckets themselves public or unencrypted. Without these, a breach is invisible — A09.
- **Public compute:** instances/functions with public IPs and open groups; serverless functions with over-broad execution roles or env-var secrets.

## Secrets & identity

- **Hardcoded credentials in IaC:** access keys, DB passwords, tokens as literals or `default` values in variables; secrets committed in `terraform.tfvars`. → `secure-coding.md`.
- **State files with secrets:** `terraform.tfstate` stores resource attributes *including secrets* in plaintext — a committed or public-bucket state file is a credential leak. Backend must be remote, encrypted, access-controlled, with state locking.
- **Prefer managed identity over static keys:** IAM roles / workload identity / managed identities instead of long-lived access keys in env or code. Static keys that never rotate are a finding.
- **Secrets management:** secrets sourced from Secrets Manager/Parameter Store/Key Vault/Secret Manager, not env literals.

## Networking & segmentation

- Databases and internal services in private subnets, not public; no public IP unless required.
- Default VPC / default security group used for sensitive workloads (often over-permissive).
- Peering/transit and cross-account trust scoped tightly; no `0.0.0.0/0` egress where it enables exfiltration if it's cheap to restrict.
- Public endpoints (API Gateway, LB) fronted by WAF where the threat model warrants.

## Platform specifics (spot-check)

- **AWS:** S3 public-access-block at account + bucket level; IMDSv2 enforced (`http_tokens = required`) to blunt SSRF→credential theft; KMS key policies not wide-open; root account MFA; no long-lived access keys on the root user.
- **GCP:** no `allUsers`/`allAuthenticatedUsers` IAM bindings; service-account key files avoided (use workload identity); default service account not broadly privileged; org policies enforced.
- **Azure:** no `Contributor`/`Owner` at broad scope; storage account "secure transfer required" on; NSGs not open to Any; Key Vault access policies/RBAC scoped; managed identities over service principals with secrets.

## Reporting

Per finding: the resource block (file:line) or live resource, the exposure it creates (who can reach what), and the fix as a concrete config change (`block_public_access = true`, scope the IAM action/resource, restrict the CIDR, enable encryption/logging). If you only saw IaC (not the live account), say so — drift means the deployed state may differ; recommend a Trivy/Checkov/tfsec scan and a live-account review to confirm. Rank by exposure: internet-reachable + sensitive-data outranks a missing tag or an internal encryption gap.
