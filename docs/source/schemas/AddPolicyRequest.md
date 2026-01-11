(addpolicyrequest)=

# AddPolicyRequest

| Field | Type | Required | Description |
|------|------|----------|-------------|
| policyNumber | string | Yes | Details of policyNumber |
| insured | object of [`insured`](addpolicyrequest_insured) | Yes | Insured party personal and contact details |
| vehicle | object of [`vehicle`](addpolicyrequest_vehicle) | Yes | Vehicle details covered by the policy |
| validity | object of [`validity`](addpolicyrequest_validity) | Yes | Policy validity period including start and end dates |
| insuredValue | number | Yes | Total insured value of the policy |
| deductibleValue | number | Yes | Deductible amount applicable to the policy |