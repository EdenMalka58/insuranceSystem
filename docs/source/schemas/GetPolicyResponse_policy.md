(getpolicyresponse_policy)=

# GetPolicyResponse_policy

| Field | Type | Required | Description |
|------|------|----------|-------------|
| policyNumber | string | No | Details of policyNumber |
| insured | object of [`insured`](getpolicyresponse_policy_insured) | No | Insured party personal and contact details |
| vehicle | object of [`vehicle`](getpolicyresponse_policy_vehicle) | No | Vehicle details covered by the policy |
| validity | object of [`validity`](getpolicyresponse_policy_validity) | No | Policy validity period including start and end dates |
| insuredValue | number | No | Total insured value of the policy |
| deductibleValue | number | No | Deductible amount applicable to the policy |
| createdAt | string | No | Timestamp when the record was created |