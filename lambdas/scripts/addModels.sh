set -e
API_ID=azy4fomrz8

echo "Add Policy models"
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name AddPolicyRequest \
  --content-type application/json \
  --description "Request schema for creating an insurance policy" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "AddPolicyRequest",
    "type": "object",
    "required": [
      "policyNumber",
      "insured",
      "vehicle",
      "validity",
      "insuredValue",
      "deductibleValue"
    ],
    "properties": {
      "policyNumber": { "type": "string" },
      "insured": {
        "type": "object",
        "required": ["name", "idNumber"],
        "properties": {
          "name": { "type": "string" },
          "email": { "type": "string" },
          "phone": { "type": "string" },
          "idNumber": { "type": "string" }
        }
      },
      "vehicle": {
        "type": "object",
        "required": ["model", "year", "plateNumber"],
        "properties": {
          "model": { "type": "string" },
          "year": { "type": "integer" },
          "plateNumber": { "type": "string" }
        }
      },
      "validity": {
        "type": "object",
        "required": ["start", "end"],
        "properties": {
          "start": { "type": "string", "format": "date" },
          "end": { "type": "string", "format": "date" }
        }
      },
      "insuredValue": { "type": "number" },
      "deductibleValue": { "type": "number" }
    }
  }'

aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name AddPolicyResponse \
  --content-type application/json \
  --description "Success response for policy creation" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "AddPolicyResponse",
    "type": "object",
    "properties": {
      "message": { "type": "string" },
      "policyNumber": { "type": "string" }
    }
  }'

echo "Add Claim models"
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name AddClaimRequest \
  --content-type application/json \
  --description "Request schema for creating an insurance claim" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "AddClaimRequest",
    "type": "object",
    "required": [
      "policyNumber",
      "claimNumber",
      "claimDate",
      "description"
    ],
    "properties": {
      "policyNumber": { "type": "string" },
      "claimNumber": { "type": "string" },
      "claimDate": { "type": "string", "format": "date" },
      "description": { "type": "string" },
      "assessmentValue": { "type": "number" },
      "approvedValue": { "type": "number" },
      "damageAreas": {
        "type": "array",
        "items": { "type": "string" }
      }
    }
  }'

aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name AddClaimResponse \
  --content-type application/json \
  --description "Success response for claim creation" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "AddClaimResponse",
    "type": "object",
    "properties": {
      "message": { "type": "string" },
      "claimNumber": { "type": "string" },
      "policyNumber": { "type": "string" },
      "emailSent": { "type": "boolean" }
    }
  }'

echo "Add Claim Damages models"
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name AddClaimDamagesRequest \
  --content-type application/json \
  --description "Request schema for adding damage areas to a claim using a token" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "AddClaimDamagesRequest",
    "type": "object",
    "required": ["damageAreas"],
    "properties": {
      "damageAreas": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": ["area", "severity"],
          "properties": {
            "area": {
              "type": "string",
              "enum": [
                "front","frontLeft","frontRight",
                "rear","rearRight","rearLeft",
                "rightSide","rightFrontSide","rightRearSide",
                "leftSide","leftFrontSide","leftRearSide"
              ]
            },
            "severity": {
              "type": "string",
              "enum": ["slight", "medium", "extensive"]
            }
          }
        }
      }
    }
  }'

aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name AddClaimDamagesResponse \
  --content-type application/json \
  --description "Success response after damage evaluation" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "AddClaimDamagesResponse",
    "type": "object",
    "properties": {
      "claimNumber": { "type": "string" },
      "assessmentValue": { "type": "number" },
      "approvedValue": { "type": "number" },
      "status": {
        "type": "string",
        "enum": ["approved", "rejected"]
      },
      "damageAreas": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "area": { "type": "string" },
            "severity": { "type": "string" },
            "estimatedCost": { "type": "number" }
          }
        }
      }
    }
  }'

echo "Delete Policy models" 
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name DeletePolicyResponse \
  --content-type application/json \
  --description "Success response for deleting a policy" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "DeletePolicyResponse",
    "type": "object",
    "properties": {
      "message": { "type": "string" }
    }
  }'

echo "Get Admin Dashboard models" 
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name GetAdminDashboardResponse \
  --content-type application/json \
  --description "Response schema for admin dashboard statistics" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetAdminDashboardResponse",
    "type": "object",
    "properties": {
      "year": { "type": "integer" },
      "counters": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": { "type": "string" },
            "title": { "type": "string" },
            "count": { "type": "integer" },
            "amount": { "type": "integer" },
            "color": { "type": "string" },
            "drilldown": {
              "type": "object",
              "properties": {
                "type": { "type": "string" },
                "value": { "type": "string" }
              }
            }
          }
        }
      },
      "claimsOverview": {
        "type": "object",
        "properties": {
          "type": { "type": "string" },
          "labels": { "type": "array", "items": { "type": "string" } },
          "datasets": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "label": { "type": "string" },
                "data": { "type": "array", "items": { "type": "integer" } },
                "borderColor": { "type": "string" },
                "backgroundColor": { "type": "string" },
                "drilldownType": { "type": "string" },
                "fill": { "type": "boolean" }
              }
            }
          }
        }
      },
      "activity": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "label": { "type": "string" },
            "count": { "type": "integer" },
            "color": { "type": "string" },
            "type": { "type": "string" }
          }
        }
      }
    }
  }'

echo "Get Admin Dashboard Drill-down models"
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name GetAdminDashboardDrilldownRequest \
  --content-type application/json \
  --description "Query parameters for admin drilldown" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetAdminDashboardDrilldownRequest",
    "type": "object",
    "properties": {
      "type": {
        "type": "string",
        "enum": [
          "policies",
          "claimsByStatus",
          "damagesReported",
          "autoApproved",
          "manualApproved",
          "waitingClaims",
          "approvedClaimsByMonth",
          "rejectedClaimsByMonth"
        ]
      },
      "value": { "type": "string" },
      "year": { "type": "integer" }
    }
  }'

aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name GetAdminDashboardDrilldownResponse \
  --content-type application/json \
  --description "Drilldown results for admin queries: items can be policy or claim records" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetAdminDashboardDrilldownResponse",
    "type": "array",
    "items": {
      "oneOf": [
        {
          "type": "object",
          "title": "Policy",
          "properties": {
            "PK": { "type": "string" },
            "SK": { "type": "string" },
            "entityType": { "type": "string", "enum": ["POLICY"] },
            "policyNumber": { "type": "string" },
            "insured": {
              "type": "object",
              "properties": {
                "name": { "type": "string" },
                "email": { "type": "string" },
                "phone": { "type": "string" },
                "idNumber": { "type": "string" }
              }
            },
            "vehicle": {
              "type": "object",
              "properties": {
                "model": { "type": "string" },
                "year": { "type": "integer" },
                "plateNumber": { "type": "string" }
              }
            },
            "validity": {
              "type": "object",
              "properties": {
                "start": { "type": "string" },
                "end": { "type": "string" }
              }
            },
            "insuredValue": { "type": "number" },
            "deductibleValue": { "type": "number" },
            "createdAt": { "type": "string" }
          }
        },
        {
          "type": "object",
          "title": "Claim",
          "properties": {
            "PK": { "type": "string" },
            "SK": { "type": "string" },
            "entityType": { "type": "string", "enum": ["POLICY_CLAIM"] },
            "claimNumber": { "type": "string" },
            "policyNumber": { "type": "string" },
            "claimDate": { "type": "string" },
            "description": { "type": "string" },
            "status": { "type": "string", "enum": ["opened","approved","rejected"] },
            "approvedAction": { "type": "string" },
            "assessmentValue": { "type": "number" },
            "approvedValue": { "type": "number" },
            "damageAreas": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "area": { "type": "string" },
                  "severity": { "type": "string" },
                  "estimatedCost": { "type": "number" }
                }
              }
            },
            "createdAt": { "type": "string" },
            "updatedAt": { "type": "string" }
          }
        }
      ]
    }
  }'

echo "Get Admin Statistics models"
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name GetAdminStatisticsResponse \
  --content-type application/json \
  --description "Response schema for admin statistics and analytics charts" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetAdminStatisticsResponse",
    "type": "object",
    "properties": {
      "claimsByStatus": { "$ref": "#/definitions/chart" },
      "claimsByApprovedAction": { "$ref": "#/definitions/chart" },
      "claimsOverTime": { "$ref": "#/definitions/chart" },
      "approvedValueByMonth": { "$ref": "#/definitions/chart" },
      "policiesOverTime": { "$ref": "#/definitions/chart" },
      "claimsByVehicleYear": { "$ref": "#/definitions/chart" },
      "claimsByVehicleValue": { "$ref": "#/definitions/chart" },
      "approvalRateByDeductible": { "$ref": "#/definitions/chart" },
      "avgClaimCostByVehicleValue": { "$ref": "#/definitions/chart" },
      "deductibleVsOutcome": { "$ref": "#/definitions/chart" }
    },
    "definitions": {
      "dataset": {
        "type": "object",
        "properties": {
          "label": { "type": "string" },
          "data": { "type": "array", "items": { "type": "number" } }
        }
      },
      "chart": {
        "type": "object",
        "properties": {
          "title": { "type": "string" },
          "type": { "type": "string" },
          "data": {
            "type": "object",
            "properties": {
              "labels": { "type": "array", "items": { "type": "string" } },
              "datasets": { "type": "array", "items": { "$ref": "#/definitions/dataset" } }
            }
          },
          "options": { "type": "object" },
          "drilldown": {
            "type": "object",
            "properties": {
              "enabled": { "type": "boolean" },
              "key": { "type": "string" },
              "endpoint": { "type": "string" }
            }
          }
        }
      }
    }
  }'

echo "Get Policies models" 
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name GetPoliciesRequest \
  --content-type application/json \
  --description "Request for listing policies with optional search and pagination" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetPoliciesRequest",
    "type": "object",
    "properties": {
      "query": { "type": "string" },
      "page": { "type": "integer", "minimum": 1 },
      "pageSize": { "type": "integer", "minimum": 1, "maximum": 50 }
    }
  }'

aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name GetPoliciesResponse \
  --content-type application/json \
  --description "Response for list policies endpoint" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetPoliciesResponse",
    "type": "object",
    "properties": {
      "items": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "policyNumber": { "type": "string" },
            "insured": {
              "type": "object",
              "properties": {
                "name": { "type": "string" },
                "email": { "type": "string" },
                "phone": { "type": "string" },
                "idNumber": { "type": "string" }
              }
            },
            "vehicle": {
              "type": "object",
              "properties": {
                "model": { "type": "string" },
                "year": { "type": "integer" },
                "plateNumber": { "type": "string" }
              }
            },
            "validity": {
              "type": "object",
              "properties": {
                "start": { "type": "string" },
                "end": { "type": "string" }
              }
            },
            "insuredValue": { "type": "number" },
            "deductibleValue": { "type": "number" },
            "createdAt": { "type": "string" }
          }
        }
      },
      "page": { "type": "integer" },
      "pageSize": { "type": "integer" },
      "total": { "type": "integer" },
      "hasNext": { "type": "boolean" }
    }
  }'

echo "Get Policy models"
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name GetPolicyRequest \
  --content-type application/json \
  --description "Request to get a policy and its claims (policyNumber path/query parameter)" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetPolicyRequest",
    "type": "object",
    "properties": {
      "policyNumber": { "type": "string" }
    }
  }'

aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name GetPolicyResponse \
  --content-type application/json \
  --description "Response with policy and its claims" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetPolicyResponse",
    "type": "object",
    "properties": {
      "policy": {
        "type": "object",
        "properties": {
          "policyNumber": { "type": "string" },
          "insured": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "email": { "type": "string" },
              "phone": { "type": "string" },
              "idNumber": { "type": "string" }
            }
          },
          "vehicle": {
            "type": "object",
            "properties": {
              "model": { "type": "string" },
              "year": { "type": "integer" },
              "plateNumber": { "type": "string" }
            }
          },
          "validity": {
            "type": "object",
            "properties": {
              "start": { "type": "string" },
              "end": { "type": "string" }
            }
          },
          "insuredValue": { "type": "number" },
          "deductibleValue": { "type": "number" },
          "createdAt": { "type": "string" }
        }
      },
      "claimsCount": { "type": "integer" },
      "claims": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "claimNumber": { "type": "string" },
            "claimDate": { "type": "string" },
            "description": { "type": "string" },
            "status": { "type": "string" },
            "approvedAction": { "type": "string" },
            "assessmentValue": { "type": "number" },
            "approvedValue": { "type": "number" },
            "damageAreas": {
              "type": "array",
              "items": { "type": "object" }
            },
            "createdAt": { "type": "string" },
            "updatedAt": { "type": "string" }
          }
        }
      }
    }
  }'

echo "Get Token Data models"
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name GetTokenDataRequest \
  --content-type application/json \
  --description "Request with claim access token" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetTokenDataRequest",
    "type": "object",
    "properties": {
      "tokenId": { "type": "string" }
    }
  }'

aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name GetTokenDataResponse \
  --content-type application/json \
  --description "Response with policy data for the claim token" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetTokenDataResponse",
    "type": "object",
    "properties": {
      "policyNumber": { "type": "string" },
      "claimNumber": { "type": "string" },
      "insured": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "email": { "type": "string" },
          "phone": { "type": "string" },
          "idNumber": { "type": "string" }
        }
      },
      "vehicle": {
        "type": "object",
        "properties": {
          "model": { "type": "string" },
          "year": { "type": "integer" },
          "plateNumber": { "type": "string" }
        }
      }
    }
  }'

echo "Update Claim Status models"
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name UpdateClaimStatusRequest \
  --content-type application/json \
  --description "Request to manually approve or reject a claim" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "UpdateClaimStatusRequest",
    "type": "object",
    "properties": {
      "policyNumber": { "type": "string" },
      "claimNumber": { "type": "string" },
      "isApproved": { "type": "boolean" }
    },
    "required": ["policyNumber","claimNumber","isApproved"]
  }'

aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name UpdateClaimStatusResponse \
  --content-type application/json \
  --description "Response after manually approving or rejecting a claim" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "UpdateClaimStatusResponse",
    "type": "object",
    "properties": {
      "message": { "type": "string" },
      "policyNumber": { "type": "string" },
      "claimNumber": { "type": "string" },
      "approvedValue": { "type": "number" },
      "approvedAction": { "type": "string" }
    }
  }'

echo "Update policy models"
aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name UpdatePolicyRequest \
  --content-type application/json \
  --description "Request to update policy metadata" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "UpdatePolicyRequest",
    "type": "object",
    "properties": {
      "insuredValue": { "type": "number" },
      "deductibleValue": { "type": "number" },
      "insured": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "email": { "type": "string" },
          "phone": { "type": "string" }
        }
      },
      "vehicle": {
        "type": "object",
        "properties": {
          "make": { "type": "string" },
          "model": { "type": "string" },
          "year": { "type": "integer" },
          "licensePlate": { "type": "string" }
        }
      },
      "validity": {
        "type": "object",
        "properties": {
          "startDate": { "type": "string" },
          "endDate": { "type": "string" }
        }
      }
    }
  }'

aws apigateway create-model \
  --rest-api-id "$API_ID" \
  --name UpdatePolicyResponse \
  --content-type application/json \
  --description "Response after updating policy metadata" \
  --schema '{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "UpdatePolicyResponse",
    "type": "object",
    "properties": {
      "message": { "type": "string" }
    }
  }'


nano addModels.sh
CTRL+X
chmod +x addModels.sh
./addModels.sh