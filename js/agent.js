let policies = [];
let currentPolicyToDelete = null;
let currentPolicyToChange = null;
let currentClaimToChange = null;
let currentClaimToChangeBtn = null;
let isEditMode = false;
let currentPage = 1;
let pageSize = 5;
let lastQuery = null;
let loadingPolicies = false;
let hasNextPage = true;

async function loadPolicies(query, reset = true) {
  if (loadingPolicies) return;
  if (!hasNextPage && !reset) return;

  loadingPolicies = true;

  if (reset) {
    currentPage = 1;
    hasNextPage = true;
    $('#policiesList').empty();
  }

  lastQuery = query;

  let url = 'policies';
  const params = [];

  if (query) params.push(`query=${encodeURIComponent(query)}`);
  params.push(`page=${currentPage}`);
  params.push(`pageSize=${pageSize}`);

  url += '?' + params.join('&');

  addSpinner('policiesListLoader');

  await apiCallAsync('GET', url, null,
    function (data) {
      const policiesList = data.items || [];

      hasNextPage = data.hasNext === true;
      displayPolicies(policiesList, !reset);

      if (hasNextPage) {
        currentPage++;
      }
    },
    function () {
      $('#policiesList').html(`
        <div class="alert alert-danger">
          <i class="fas fa-exclamation-circle"></i> Error loading policies
        </div>
      `);
    }
  );

  loadingPolicies = false;
  removeSpinner('policiesListLoader');
}

function initPaginationOnScroll() {
  $(window).on('scroll', function () {
    if (loadingPolicies) return;
    if (!hasNextPage) return;

    const scrollTop = $(window).scrollTop();
    const windowHeight = $(window).height();
    const docHeight = $(document).height();

    if (scrollTop + windowHeight >= docHeight - 100) {
      loadPolicies(lastQuery, false);
    }
  });
}

async function searchPolicies() {
  loadPolicies($('#searchInput').val().trim());
}

function displayPolicies(policiesList, isMore) {
  const container = $('#policiesList');
  if (!isMore) {
    container.empty();

    if (!policiesList || policiesList.length === 0) {
      container.html('<div class="alert alert-info">No policies found</div>');
      return;
    }
  }
  policiesList.forEach(policy => {
    const card = getPolicyDetailsHTML(policy, true);
    container.append(card);
  });
}

async function viewClaims(policyNumber) {
  const modal = new bootstrap.Modal($('#claimsListModal'));
  modal.show();
  loadPolicyClaims(policyNumber);
}

async function loadPolicyClaims(policyNumber) {
  addSpinner('claimsListContent');
  const url = `policies/${encodeURIComponent(policyNumber)}`;
  await apiCallAsync('GET', url, null, displayClaimsList, function () {
    $('#claimsListContent').html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> Error loading claims
            </div>
        `);
  })
}

function displayClaimsList(data) {
  const { policy, claimsCount, claims } = data;

  let html = `
        <div class="mb-4">
            <h5><i class="fas fa-file-contract"></i> Policy: ${policy.policyNumber}</h5>
            <div class="row">
                <div class="col-md-6">
                    <p class="mb-1"><strong>Insured:</strong> ${policy.insured.name}</p>
                    <p class="mb-1"><strong>Vehicle:</strong> ${policy.vehicle.model} (${policy.vehicle.year})</p>
                </div>
                <div class="col-md-6">
                    <p class="mb-1"><strong>Plate:</strong> ${policy.vehicle.plateNumber}</p>
                    <p class="mb-1"><strong>Total Claims:</strong> ${claimsCount}</p>
                </div>
            </div>
        </div>
        <hr>
    `;

  if (!claims || claims.length === 0) {
    html += '<div class="alert alert-info"><i class="fas fa-info-circle"></i> No claims found for this policy</div>';
  } else {
    claims.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
    html += '<h5 class="mb-3">Claims List</h5>';
    claims.forEach(claim => {
      html += getClaimDetailsHTML(claim, true, policy)
    });
  }

  $('#claimsListContent').html(html);
}

function showAddPolicy() {
  isEditMode = false;
  $('#formTitle').text('Add New Policy');
  $('#policyForm')[0].reset();

  $('#policyNumber').attr('placeholder', `POL-${new Date().getFullYear()}-`).prop("disabled", false);
  $('#searchSection').hide();
  $('#policiesSection').hide();
  $('#policyFormSection').show();
}

function editPolicy(policy) {
  isEditMode = true;
  $('#formTitle').text('Edit Policy');
  $('#policyNumber').val(policy.policyNumber).prop("disabled", true);
  $('#insuredName').val(policy.insured.name);
  $('#insuredId').val(policy.insured.idNumber);
  $('#insuredEmail').val(policy.insured.email);
  $('#insuredPhone').val(policy.insured.phone);
  $('#vehicleModel').val(policy.vehicle.model);
  $('#vehicleYear').val(policy.vehicle.year);
  $('#plateNumber').val(policy.vehicle.plateNumber);
  $('#validityStart').val(policy.validity.start);
  $('#validityEnd').val(policy.validity.end);
  $('#insuredValue').val(policy.insuredValue);
  $('#deductibleValue').val(policy.deductibleValue);

  $('#searchSection').hide();
  $('#policiesSection').hide();
  $('#policyFormSection').show();
}

function cancelForm() {
  $('#searchSection').show();
  $('#policiesSection').show();
  $('#policyFormSection').hide();
  $('#policyForm')[0].reset();
}

async function savePolicy() {
  const policyData = {
    policyNumber: $('#policyNumber').val(),
    insured: {
      name: $('#insuredName').val(),
      email: $('#insuredEmail').val(),
      phone: $('#insuredPhone').val(),
      idNumber: $('#insuredId').val()
    },
    vehicle: {
      model: $('#vehicleModel').val(),
      year: parseInt($('#vehicleYear').val()),
      plateNumber: $('#plateNumber').val()
    },
    validity: {
      start: $('#validityStart').val(),
      end: $('#validityEnd').val()
    },
    insuredValue: parseFloat($('#insuredValue').val()),
    deductibleValue: parseFloat($('#deductibleValue').val())
  };

  
  const method = isEditMode ? 'PUT' : 'POST';
  const url = isEditMode ? `policies/${policyData.policyNumber}` : 'policies';
    
  await apiCallAsync(method, url, policyData,
    function () {
      showAlert(isEditMode ? 'Policy updated successfully' : 'Policy added successfully', 'success', 'Success');
      cancelForm();
      loadPolicies();
    },
    function () {
      showAlert('Error saving policy', 'error', 'Error');
    }, $('#save-policy-btn'))
}

function openClaimModal(policyNumber) {
  $('#claimPolicyNumber').val(policyNumber);
  $('#claimForm')[0].reset();
  $('#claimNumber').attr('placeholder', `CLM-${new Date().getFullYear()}-`)
  $('#claimDate').val(new Date().toISOString().split('T')[0]);
  new bootstrap.Modal($('#claimModal')).show();
}

async function submitClaim(e) {
  const claimData = {
    policyNumber: $('#claimPolicyNumber').val(),
    claimNumber: $('#claimNumber').val(),
    claimDate: $('#claimDate').val(),
    description: $('#claimDescription').val()
  };
  if (!claimData.policyNumber || !claimData.claimNumber || !claimData.claimDate || !claimData.description) {
    showAlert('Please fill the missing fields!', 'warning', 'Missing fields');
    return false;
  }

  await apiCallAsync('POST', 'claims', claimData, function (data) {
    const successMessage = '<span>Claim opened successfully</span><br/>'
    const linkSentMessage = data.emailSent ? '<span>A link is sent to the insured for reporting vehicle damage.</span>' : ''
    showAlert(`${successMessage}${linkSentMessage}`, 'success', 'Success');
    bootstrap.Modal.getInstance($('#claimModal')).hide();
  }, function (error) {
    showAlert(error.error, 'error', 'Error opening claim');
  }, $('#save-claim-btn'))
}

function deletePolicy(policyNumber) {
  currentPolicyToDelete = policyNumber;
  $('#deletePolicyNumber').text(policyNumber);
  new bootstrap.Modal($('#deleteModal')).show();
}

async function confirmDelete() {
  await apiCallAsync('DELETE', `policies/${currentPolicyToDelete}`, null,
    function () {
      showAlert('Policy deleted successfully', 'success', 'Success');
      bootstrap.Modal.getInstance($('#deleteModal')).hide();
      loadPolicies();
    },
    function () {
      showAlert('Error deleting policy', 'error', 'Error');
    },
    $('#delete-policy-btn')
  )
}

function approveClaim(btn, policyNumber, claimNumber, assessmentValue) {
  currentPolicyToChange = policyNumber;
  currentClaimToChange = claimNumber;
  currentClaimToChangeBtn = btn;
  const approveClaimModalHeader = $('#approveClaimModalHeader').empty();
  const approveClaimModalText = $('#approveClaimModalText').empty();
  const approveClaimModalBtn = $('#approveClaimModalBtn').empty();
  approveClaimModalHeader.html('<i class="fa-solid fa-thumbs-up"></i> Claim confirmation');
  approveClaimModalText.html(`Are you sure you want to approve claim <strong>${claimNumber}</strong> for <strong>${CURRENCY_SIGN} ${assessmentValue.toLocaleString() }</strong> ?`);
  approveClaimModalBtn.off('click').on('click', function () { confirmClaimApprove(true) }).text('Approve Claim')
  new bootstrap.Modal($('#approveClaimModal')).show();
}

function rejectClaim(btn, policyNumber, claimNumber, assessmentValue) {
  currentPolicyToChange = policyNumber;
  currentClaimToChange = claimNumber;
  currentClaimToChangeBtn = btn;
  const approveClaimModalHeader = $('#approveClaimModalHeader').empty();
  const approveClaimModalText = $('#approveClaimModalText').empty();
  const approveClaimModalBtn = $('#approveClaimModalBtn').empty();
  approveClaimModalHeader.html('<i class="fa-solid fa-thumbs-down"></i> Claim rejection');
  approveClaimModalText.html(`Are you sure you want to reject claim <strong>${claimNumber}</strong> for <strong>${CURRENCY_SIGN} ${assessmentValue.toLocaleString()}</strong> ?`);
  approveClaimModalBtn.off('click').on('click', function () { confirmClaimApprove(false) }).text('Reject Claim')
  new bootstrap.Modal($('#approveClaimModal')).show();
}


async function confirmClaimApprove(isApproved) {
  const claimData = {
    policyNumber: currentPolicyToChange,
    claimNumber: currentClaimToChange,
    isApproved: isApproved
  };

  await apiCallAsync('PUT', 'claims', claimData, function (data) {
    showAlert(isApproved ? 'Claim approved successfully' : 'Claim rejected successfully', 'success', 'Success');
    bootstrap.Modal.getInstance($('#approveClaimModal')).hide();
    loadPolicyClaims(currentPolicyToChange);
  }, function () {
    showAlert('Error approving claim', 'error', 'Error');
  }, currentClaimToChangeBtn)
}

