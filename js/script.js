const BASE_API = "https://azy4fomrz8.execute-api.us-east-1.amazonaws.com/prod";
const USER_TOKEN_STIRAGE_KEY = 'token';
const CURRENCY_SIGN = "$"

const CLAIM_STATUS_OPENED = "opened";
const CLAIM_STATUS_REJECTED = "rejected";
const CLAIM_STATUS_APPROVED = "approved";

const APPROVED_ACTION_INITIALLY = "initially";
const APPROVED_ACTION_WAITING = "waiting";
const APPROVED_ACTION_AUTOMATICALLY = "automatically";
const APPROVED_ACTION_MANUALLY = "manually";

async function apiCallAsync(method, url, data, onSuccess, onError, btn) {
  try {
    setButtonLoading(btn)
    const res = await fetch(`${BASE_API}/${url}`, {
      method: method,
      headers: {
        "Content-Type": "application/json",
        Authorization: localStorage.getItem(USER_TOKEN_STIRAGE_KEY) || ''
      },
      body: data ? JSON.stringify(data) : null
    });
    resetButtonLoading(btn)
    const result = await res.json();
    if (res.ok) { // Status 200
      onSuccess && onSuccess(result);
      return result;
    }
    else { 
      console.error(result);
      onError && onError(result);
      return result;
    }
  }
  catch (error) {
    console.error(error);
    onError && onError(error);
    return null;
  }
}

//async function callWebMethod() {
//  $.ajax({
//    url: `${BASE_API}/admin/statistics/drilldown`,
//    method: "GET",
//    headers: {
//      "Authorization": localStorage.getItem("idToken") || ""
//    },
//    data: {
//      type: type,
//      value: value
//    },
//    success: data => {
//      $("#drilldownContent").text(JSON.stringify(data, null, 2));
//      new bootstrap.Modal("#drilldownModal").show();
//    },
//    error: () => alert("Failed loading drilldown data")
//  });
//}

function setButtonLoading(btn) {
  if (!btn)
    return;

  var $btn = $(btn);
  if (!$btn.button || $btn.length == 0)
    return;
  try {
    $btn.prop("disabled", true);
    $btn.find('.fa').hide();
    $btn.prepend($('<span />').addClass('spinner-border spinner-border-sm'), ' ');
  }
  catch (err) { }
}

function resetButtonLoading(btn) {
  if (!btn)
    return;

  var $btn = $(btn);
  if (!$btn.button || $btn.length == 0)
    return;
  try {
    $btn.find('.spinner-border').remove();
    $btn.find('.fa').show();
    $btn.prop("disabled", false);
  }
  catch (err) { }
}



// Alert function
function showAlert(message, type = 'info', title = 'Notification') {
    const alertTypes = {
        success: 'alert-success',
        error: 'alert-danger',
        warning: 'alert-warning',
        info: 'alert-info'
    };

    const alertClass = alertTypes[type] || alertTypes.info;
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    const iconClass = icons[type] || icons.info;

    $('#alertModalTitle').text(title);
    $('#alertModalContent').html(`
                <div class="alert ${alertClass} mb-0" role="alert">
                    <i class="fas ${iconClass} me-2"></i>${message}
                </div>
            `);
    new bootstrap.Modal($('#alertModal')).show();
}


function addSpinner(elementId) {
    $(`#${elementId}`).html(`
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `);

}

function removeSpinner(elementId) {
  $(`#${elementId}`).empty();
}



const AREA_FRONT = "front";
const AREA_FRONT_LEFT = "frontLeft";
const AREA_FRONT_RIGHT = "frontRight";
const AREA_REAR = "rear";
const AREA_REAR_RIGHT = "rearRight";
const AREA_REAR_LEFT = "rearLeft";
const AREA_RIGHT_SIDE = "rightSide";
const AREA_RIGHT_FRONT_SIDE = "rightFrontSide";
const AREA_RIGHT_REAR_SIDE = "rightRearSide";
const AREA_LEFT_SIDE = "leftSide";
const AREA_LEFT_FRONT_SIDE = "leftFrontSide";
const AREA_LEFT_REAR_SIDE = "leftRearSide";

const SEVERITY_SLIGHT = "slight"; //1
const SEVERITY_MEDIUM = "medium"; //2
const SEVERITY_EXTENSIVE = "extensive"; //3
const SEVERITY_NONE = "empty"; //4

var impactAreasTable = [
  { id: AREA_FRONT, x: "86%", y: "48%", desc: "Front" },
  { id: AREA_FRONT_LEFT, x: "78%", y: "21%", desc: "Front Left" },
  { id: AREA_FRONT_RIGHT, x: "78%", y: "75%", desc: "Front Right" },
  { id: AREA_REAR, x: "10%", y: "48%", desc: "Rear" },
  { id: AREA_REAR_RIGHT, x: "16%", y: "74%", desc: "Rear Right" },
  { id: AREA_REAR_LEFT, x: "16%", y: "22%", desc: "Rear Left" },
  { id: AREA_RIGHT_SIDE, x: "48%", y: "75%", desc: "Right Side" },
  { id: AREA_RIGHT_FRONT_SIDE, x: "63%", y: "75%", desc: "Right Front Side" },
  { id: AREA_RIGHT_REAR_SIDE, x: "32%", y: "75%", desc: "Right Rear Side" },
  { id: AREA_LEFT_SIDE, x: "48%", y: "21%", desc: "Left Side" },
  { id: AREA_LEFT_FRONT_SIDE, x: "63%", y: "21%", desc: "Left Front Side" },
  { id: AREA_LEFT_REAR_SIDE, x: "32%", y: "21%", desc: "Left Rear Side" },
];
function getAreaDesc(areaId) {
  const area = impactAreasTable.find(area => area.id === areaId);
  return area ? area.desc : areaId; 
}

function getLevelDesc(levelId) {
    switch (levelId) {
        case SEVERITY_SLIGHT:
            return "Slight";
        case SEVERITY_MEDIUM:
            return "Medium";
        case SEVERITY_EXTENSIVE:
            return "Extensive";
    }
    return levelId;
}


function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US');
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString('en-US');
}

function getPolicyDetailsHTML(policy, asAgent) {
  if (!policy) return '';
  const isActive = new Date(policy.validity.end) > new Date();
  const statusClass = isActive ? 'status-active' : 'status-expired';
  const statusText = isActive ? 'Active' : 'Expired';

  return `
        <div class="policy-card">
            <div class="policy-header">
                <div class="policy-number">
                    <i class="fas fa-file-contract"></i> ${policy.policyNumber}
                </div>
                <span class="policy-status ${statusClass}">${statusText}</span>
            </div>
            <div class="policy-info">
                <div class="info-item">
                    <i class="fas fa-user"></i>
                    <strong>Insured:</strong>&nbsp;${policy.insured.name}
                </div>
                <div class="info-item">
                    <i class="fas fa-id-card"></i>
                    <strong>ID:</strong>&nbsp;${policy.insured.idNumber}
                </div>
                <div class="info-item">
                    <i class="fas fa-envelope"></i>
                    <strong>Email:</strong>&nbsp;${policy.insured.email}
                </div>
                <div class="info-item">
                    <i class="fas fa-phone"></i>
                    <strong>Phone:</strong>&nbsp;${policy.insured.phone}
                </div>
                <div class="info-item">
                    <i class="fas fa-car"></i>
                    <strong>Vehicle:</strong>&nbsp;${policy.vehicle.model} (${policy.vehicle.year})
                </div>
                <div class="info-item">
                    <i class="fas fa-hashtag"></i>
                    <strong>Plate:</strong>&nbsp;${policy.vehicle.plateNumber}
                </div>
                <div class="info-item">
                    <i class="fas fa-calendar-check"></i>
                    <strong>Validity:</strong>&nbsp;${formatDate(policy.validity.start)} - ${formatDate(policy.validity.end)}
                </div>
                <div class="info-item">
                    <i class="fas fa-coins"></i>
                    <strong>Value:</strong>&nbsp;${CURRENCY_SIGN}${policy.insuredValue.toLocaleString()}
                </div>
                <div class="info-item">
                    <i class="fas fa-hand-holding-usd"></i>
                    <strong>Deductible:</strong>&nbsp;${CURRENCY_SIGN}${policy.deductibleValue.toLocaleString()}
                </div>
            </div>
            ${asAgent ? `<div class="d-flex w-100 justify-content-between">
                <div class="action-buttons">
                    <button class="btn btn-primary btn-sm" onclick='openClaimModal(${JSON.stringify(policy.policyNumber)})'>
                        <i class="fas fa-file-medical"></i> Open Claim
                    </button>
                    <button class="btn btn-light btn-sm" onclick='viewClaims(${JSON.stringify(policy.policyNumber)})'>
                        <i class="fas fa-list"></i> Claims
                    </button>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-light btn-sm" onclick='editPolicy(${JSON.stringify(policy)})'>
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-light btn-sm" onclick='deletePolicy(${JSON.stringify(policy.policyNumber)})'>
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>` : ``}
        </div>
    `;

}

function getClaimDetailsHTML(claim, asAgent, policy) {
  if (!claim) return '';

  const statusClass = `status-${claim.status}`;
  return `
        <div class="claim-item">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                    <h6 class="mb-1">
                        <i class="fas fa-hashtag"></i> ${claim.claimNumber}
                    </h6>
                    <small class="text-muted">
                        <i class="fas fa-calendar"></i> ${formatDate(claim.claimDate)}
                    </small>
                </div>
                <span class="claim-status-badge ${statusClass}">
                    ${claim.status.toUpperCase()}
                </span>
            </div>
                    
            <p><strong>Description:</strong> ${claim.description}</p>
                    
            <div class="row mb-2">
                <div class="col-md-6">
                    <small><strong>Assessment:</strong> ${CURRENCY_SIGN}${claim.assessmentValue ? claim.assessmentValue.toLocaleString() : 'N/A'}</small>
                </div>
                <div class="col-md-6">
                    <small><strong>Approved:</strong> ${CURRENCY_SIGN}${claim.approvedValue ? claim.approvedValue.toLocaleString() : 'N/A'}</small>
                </div>
            </div>
                    
            <div class="row mb-2">
                <div class="col-md-6">
                    <small><strong>Approved action:</strong> ${claim.approvedAction}</small>
                </div>
                <div class="col-md-6">
                    ${asAgent && claim.approvedAction === APPROVED_ACTION_WAITING ? `
                      <button class="btn btn-primary btn-sm me-2"
                        onclick='approveClaim($(this),${JSON.stringify(policy.policyNumber)}, ${JSON.stringify(claim.claimNumber)}, ${JSON.stringify(claim.assessmentValue)})'>
                        <i class="fa-solid fa-thumbs-up"></i> Approve claim
                      </button>
                      <button class="btn btn-warning btn-sm"
                        onclick='rejectClaim($(this),${JSON.stringify(policy.policyNumber)}, ${JSON.stringify(claim.claimNumber)}, ${JSON.stringify(claim.assessmentValue)})'>
                        <i class="fa-solid fa-thumbs-down"></i> Reject claim
                      </button>
                    ` : ``}
                </div>
            </div>
                    
            ${claim.damageAreas && claim.damageAreas.length > 0 ? `
                <div class="mt-2">
                    <strong class="d-block mb-2"><i class="fas fa-tools"></i> Damage Areas:</strong>
                    ${claim.damageAreas.map(area => `
                        <div class="damage-area-item">
                            <div class="row">
                                <div class="col-md-4">
                                    <small><strong>Area:</strong> ${getAreaDesc(area.area)}</small>
                                </div>
                                <div class="col-md-4">
                                    <small><strong>Severity:</strong> ${getLevelDesc(area.severity)}</small>
                                </div>
                                <div class="col-md-4">
                                    <small><strong>Est. Cost:</strong> ${area.estimatedCost ? CURRENCY_SIGN + ' ' + area.estimatedCost.toLocaleString() : 'N/A'}</small>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="d-flex justify-content-center align-items-center mb-2">
                  <div class="damages-image-container">
                    <img src="/images/damagesCar.jpg" alt="Impacts Map" class="damages-image" onLoad='markClaimDamagesImage(${`$(this)`}, ${JSON.stringify(claim.damageAreas)})''>
                  </div>
                </div>
            ` : ''}
                    
            <div class="mt-2">
                <small class="text-muted">
                    <i class="fas fa-clock"></i> Created: ${formatDateTime(claim.createdAt)} | 
                    Updated: ${formatDateTime(claim.updatedAt)}
                </small>
            </div>
        </div>
    `;
}

function markClaimDamagesImage(image, damages) {
  var container = image.parent();
  $.each(impactAreasTable, function (i, area) {
    var isSelected = damages && damages.find(d => d.area == area.id);
    if (isSelected)
      $("<img/>")
        .attr("src", '/images/' + area.id + ".png")
        .addClass("damages-image damages-image-area")
        .appendTo(container);
  });
}


function getUserTokenData() {
  const idToken = localStorage.getItem(USER_TOKEN_STIRAGE_KEY);
  if (idToken) {
    const payload = JSON.parse(atob(idToken.split('.')[1]));
    return payload;
  }
  return null;
}

function getUserEmail() {
  const user = getUserTokenData();
  if (user)
    return user.email;
}

function getUserGroup() {
  const user = getUserTokenData();
  //if (user)
  //  return user.cognito: groups

}

let isLoggedIn = false;

function toggleUserState() {
  isLoggedIn = !isLoggedIn;
  updateNavbar();
}

function updateNavbar() {
  const userDropdown = document.getElementById('userProfileDropdown');
  const signInLink = document.getElementById('signInLink');
  const signUpLink = document.getElementById('signUpLink');

  const userImage = $('.user-profile-img');
  const userName = $('.user-name');

  const user = getUserTokenData();
  isLoggedIn = user != null;
  if (isLoggedIn) {
    userName.text(user.email);
    userImage.attr('src', `https://ui-avatars.com/api/?name=${user.email}&background=0d6efd&color=fff`)
    userDropdown.style.display = 'block';
    signInLink.style.display = 'none';
    signUpLink.style.display = 'none';
  } else {
    userDropdown.style.display = 'none';
    signInLink.style.display = 'block';
    signUpLink.style.display = 'block';
  }
}

function handleSignIn(event) {
  event.preventDefault();
  alert('Sign In clicked - integrate with your authentication system');
}

function handleSignUp(event) {
  event.preventDefault();
  alert('Sign Up clicked - integrate with your authentication system');
}

function handleLogout(event) {
  event.preventDefault();
  if (confirm('Are you sure you want to sign out?')) {
    isLoggedIn = false;
    updateNavbar();
    alert('Signed out successfully');
  }
}