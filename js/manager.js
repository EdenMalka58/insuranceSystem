/* Dashboard functions */
let chartInstance = null;
// Color mapping for counters
const colorMap = {
  primary: { bg: 'bg-primary', text: 'text-primary', icon: 'fa-solid fa-file-lines' },
  success: { bg: 'bg-success', text: 'text-success', icon: 'fa-solid fa-circle-check' },
  warning: { bg: 'bg-warning', text: 'text-warning', icon: 'fa-solid fa-clock' },
  danger: { bg: 'bg-danger', text: 'text-danger', icon: 'fa-solid fa-circle-xmark' },
  info: { bg: 'bg-info', text: 'text-info', icon: 'fa-solid fa-circle-info' }
};

function showLoader() {
  $('#dashboard-loader').show();
}

function hideLoader() {
  $('#dashboard-loader').hide();
}
function initYearSelector() {
  const year = new Date().getFullYear();
  for (let i = 0; i < 3; i++) {
    $("#yearSelector").append(`<option value="${year - i}">${year - i}${' - '}</option>`);
  }
  $("#yearSelector").change(loadDashboard);
}

function loadDashboard() {
  const year = $("#yearSelector").val();
  apiCallAsync('GET', `dashboard?year=${year}`, null, buildDashboard, function () {
    $('#countersRow').html(`
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-circle"></i> Error loading dashboard
        </div>
     `);
    hideLoader();
  });
}

function buildDashboard(data) {
  buildCounters(data.counters);
  buildChart(data.claimsOverview, data.year);
  buildActivity(data.activity);
  hideLoader();
}

function buildCounters(counters) {
  $("#countersRow").empty();

  counters.forEach(c => {
    const colors = colorMap[c.color] || colorMap.primary;

    $("#countersRow").append(`
            <div class="col-md-3">
              <div class="card stats-card" onclick="loadDrilldown('${c.drilldown.type}','${c.drilldown.value || ""}')">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 class="text-muted text-uppercase mb-2">${c.title}</h6>
                      <h2 class="mb-0">${c.count.toLocaleString()}</h2>
                    </div>
                    <div class="${colors.bg} bg-opacity-10 stats-icon">
                      <i class="${colors.icon} display-6 ${colors.text}"></i>
                    </div>
                  </div>
                  <div class="mt-2">
                    <small class="text-muted">Amount: $${c.amount.toLocaleString()}</small>
                  </div>
                </div>
              </div>
            </div>
          `);
  });
}

function buildChart(chartData, year) {
  const ctx = document.getElementById("claimsChart");

  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: chartData.type,
    data: {
      labels: chartData.labels,
      datasets: chartData.datasets.map((dataSet) => ({ ...dataSet, fill: true }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return context.dataset.label + ': ' + context.parsed.y.toLocaleString();
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return '$' + value.toLocaleString();
            }
          }
        }
      },
      onClick: (evt, elements) => {
        if (!elements.length) return;
        const index = elements[0].index;
        const dataset = chartData.datasets[elements[0].datasetIndex];
        const month = String(index + 1).padStart(2, "0");
        loadDrilldown(dataset.drilldownType, month);
      }
    }
  });
}

function buildActivity(activity) {
  $("#activityList").empty();

  activity.forEach((a, idx) => {
    const colors = colorMap[a.color] || colorMap.primary;
    const isLast = idx === activity.length - 1;

    $("#activityList").append(`
            <div class="activity-item ${isLast ? '' : 'border-bottom'}" onclick="loadDrilldown('${a.type}')">
              <div class="d-flex align-items-center p-2">
                <div class="activity-icon ${colors.bg} bg-opacity-10 ${colors.text} me-3">
                  <i class="${colors.icon}"></i>
                </div>
                <div class="flex-grow-1">
                  <p class="mb-0 fw-semibold">${a.label}</p>
                  <small class="text-muted">${a.count} items</small>
                </div>
              </div>
            </div>
          `);
  });
}

function loadDrilldown(type, value = "") {
  addSpinner('detailsBody');
  const year = $("#yearSelector").val();
  const url = `dashboard/drilldown?type=${type}&value=${value}&year=${year}`
  apiCallAsync('GET', url, null, renderDetailsTable, function () {
    $('#detailsBody').html(`
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-circle"></i> Error loading details
        </div>
     `);
  })
}


function isVisibleField(field) {
  switch (field) {
    case 'createdAt':
    case 'claimDate':
    case 'updatedAt':
    case 'claimNumber':
    case 'policyNumber':
    case 'vehicle':
    case 'deductibleValue':
    case 'assessmentValue':
    case 'approvedValue':
    case 'insuredValue':
    case 'insured':
    case 'validity':
    case 'damageAreas':
    case 'status': return true;
    default:
    case 'description':
    case 'approvedAction': return false;
  }
}

function formatHeaderText(field) {
  switch (field) {
    case 'createdAt': return 'Created';
    case 'claimDate': return 'Date';
    case 'updatedAt': return 'Updated';
    case 'description': return 'Details';
    case 'claimNumber': return 'Claim';
    case 'policyNumber': return 'Policy';
    case 'vehicle': return 'Vehicle';
    case 'deductibleValue': return 'Deductible';
    case 'assessmentValue': return 'Assessment';
    case 'approvedValue': return 'Approved';
    case 'insuredValue': return 'Insured';
    case 'insured': return 'Insured';
    case 'validity': return 'Validity';
    case 'damageAreas': return 'Damage';
    case 'status': return 'Status';
    case 'approvedAction': return 'Action';
    default:
      return field;
  }
}

function formatFieldCell(field, value) {
  if (value === null || value === undefined || value === '') return '';

  switch (field) {
    case 'createdAt': 
    case 'claimDate':
    case 'updatedAt': return formatDate(value);
    case 'description':
    case 'claimNumber':
    case 'policyNumber': return value;
    case 'vehicle': return formatVehicle(value);
    case 'deductibleValue': 
    case 'assessmentValue':
    case 'approvedValue':
    case 'insuredValue': return formatFloat(value);
    case 'insured': return formatInsured(value);
    case 'validity': return formatValidity(value);
    case 'damageAreas': return formatDamageAreas(value);
    case 'status': return formatStatus(value);
    case 'approvedAction': return value;
    default:
      return value;
  }
}

function formatVehicle(vehicle) {
  if (vehicle) {
    const { plateNumber, model, year } = vehicle
    return `${plateNumber} - ${model} ${year}`;
  }
  return '';
}

function formatInsured(insured) {
  if (insured) {
    const { idNumber, name } = insured
    return `${idNumber} - ${name}`;
  }
  return '';
}

function formatFloat(value) {
  const num = parseFloat(value);
  if (!isNaN(num)) {
    return '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  return '';
}

function formatValidity(validity) {
  if (validity) {
    const isActive = new Date(validity.end) > new Date();
    const statusClass = isActive ? 'bg-success' : 'bg-danger';
    const statusText = isActive ? 'Active' : 'Expired';
    return '<span class="badge ' + statusClass + '">' + statusText + '</span>';
  }
  return '';
}

function formatStatus(status) {
  if (status) {
    const statusClass = `status-${status}`;
    return '<span class="claim-status-badge ' + statusClass + '">' + status.toUpperCase() + '</span>';
  }
  return '';
}

function formatDamageAreas(damageAreas) {
  if (damageAreas && damageAreas.length > 0)
    return damageAreas.length;
  return '';
}

function renderDetailsTable(data) {
  $("#detailsHeader").empty();
  $("#detailsBody").empty();
  hideLoader();
  if (!data.length) {
    $("#detailsBody").append("<tr><td colspan='100%' class='text-center text-muted py-4'>No data available</td></tr>");
    return;
  }
  
  const keys = Object.keys(data[0]).filter(k => isVisibleField(k));

  keys.forEach(k => $("#detailsHeader").append("<th>" + formatHeaderText(k) + "</th>"));

  data.forEach(row => {
    const tr = $('<tr/>').on('click', (e) => openDetailsModal(row));
    keys.forEach(k => {
      const val = formatFieldCell(k, row[k]);
      tr.append($('<td/>').html(val));
      
    });
    $("#detailsBody").append(tr);
  });
}

function openDetailsModal(data) {
  const drilldownModalTitle = $('#drilldownModalTitle').empty();
  const drilldownModalContent = $('#drilldownModalContent').empty();
  
  if (data) {
    if (data.entityType == "POLICY_CLAIM") {
      // claim record
      drilldownModalTitle.text('Cliam details')
      drilldownModalContent.html(getClaimDetailsHTML(data));
    }
    else {
      // policy record
      drilldownModalTitle.text('Policy details')
      drilldownModalContent.html(getPolicyDetailsHTML(data));
    }
  }
  new bootstrap.Modal("#drilldownModal").show();
}

/* Statistic functions */

function openStatisticsModal() {
  const drilldownModalTitle = $('#drilldownModalTitle').empty();
  const drilldownModalContent = $('#drilldownModalContent').empty();
  drilldownModalTitle.text('Statistics')
  drilldownModalContent.append('<div class="row" id="chartsContainer"></div>')
  new bootstrap.Modal("#drilldownModal").show();
  loadStatistics()
}

async function loadStatistics() {
  addSpinner('chartsContainer');
  await apiCallAsync('GET', 'statistics', null, renderCharts, function () {
    $('#chartsContainer').html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> Error loading statistics
            </div>
        `);
  })
}

function renderCharts(data) {
  const container = $("#chartsContainer");
  container.empty();

  Object.entries(data).forEach(([key, chartConfig], idx) => {
    const canvasId = `chart_${key}`;

    container.append(`
            <div class="col-xl-4 col-lg-6 col-md-12 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h6 class="card-title text-center">${chartConfig.title}</h6>
                        <canvas id="${canvasId}" height="200"></canvas>
                    </div>
                </div>
            </div>
        `);

    createChart(canvasId, key, chartConfig);
  });
}

const charts = {};
function createChart(canvasId, chartKey, config) {
  const ctx = document.getElementById(canvasId);

  charts[chartKey] = new Chart(ctx, {
    type: config.type,
    data: config.data,
    options: {
      responsive: true,
      onClick: (evt, elements) => {
        if (!elements.length || !config.drilldown?.enabled) return;

        const index = elements[0].index;
        const value = config.data.labels[index];

        loadStatisticDrilldown(config.drilldown.key, value);
      },
      plugins: {
        legend: {
          display: true,
          position: 'bottom'
        }
      }
    }
  });
}

async function loadStatisticDrilldown(type, value) {
  await apiCallAsync('GET', `statistics/drilldown?type=${type}&value=${value}`, null,
    renderDetailsTable,
    function () {
      $("#drilldownContent").text('Failed loading drilldown data');
      new bootstrap.Modal("#drilldownModal").show();
    });
}
