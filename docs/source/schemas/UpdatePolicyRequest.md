(updatepolicyrequest)=

# UpdatePolicyRequest

| Field | Type | Required | Description |
|------|------|----------|-------------|
| insuredValue | number | No | Total insured value of the policy |
| deductibleValue | number | No | Deductible amount applicable to the policy |
| insured | object of [`insured`](updatepolicyrequest_insured) | No | Insured party personal and contact details |
| vehicle | object [`vehicle`](updatepolicyrequest_vehicle) | No | Vehicle details covered by the policy |
| validity | object [`validity`](updatepolicyrequest_validity) | No | Policy validity period including start and end dates |