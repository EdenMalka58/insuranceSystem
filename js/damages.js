
var sessionTokenId = null;

function createImpactLevelRadio(impactLevel, area, imageArea, imageCircle) {
  var btnCss = "btn btn-outline-primary btn-sm";

  var radioGroup = $("<div />").addClass("btn-group").attr("role", "group");
  var slightItemRadio = $('<input type="radio"/>')
    .addClass("btn-check")
    .attr("name", "radio_" + area.id)
    .attr("id", "radio_" + area.id + "_" + SEVERITY_SLIGHT)
    .appendTo(radioGroup);
  var slightItemLabel = $("<label/>")
    .addClass(btnCss)
    .attr("for", "radio_" + area.id + "_" + SEVERITY_SLIGHT)
    .appendTo(radioGroup)
    .text("Slight");
  slightItemLabel.on("click", function () {
    onItemClicked(SEVERITY_SLIGHT);
  });
  slightItemRadio.prop("checked", impactLevel == SEVERITY_SLIGHT);

  var mediumItemRadio = $('<input type="radio"/>')
    .addClass("btn-check")
    .attr("name", "radio_" + area.id)
    .attr("id", "radio_" + area.id + "_" + SEVERITY_MEDIUM)
    .appendTo(radioGroup);
  var mediumItemLabel = $("<label/>")
    .addClass(btnCss)
    .attr("for", "radio_" + area.id + "_" + SEVERITY_MEDIUM)
    .appendTo(radioGroup)
    .text("Medium");
  mediumItemLabel.on("click", function () {
    onItemClicked(SEVERITY_MEDIUM);
  });
  mediumItemRadio.prop("checked", impactLevel == SEVERITY_MEDIUM);

  var extensiveItemRadio = $('<input type="radio"/>')
    .addClass("btn-check")
    .attr("name", "radio_" + area.id)
    .attr("id", "radio_" + area.id + "_" + SEVERITY_EXTENSIVE)
    .appendTo(radioGroup);
  var extensiveItemLabel = $("<label/>")
    .addClass(btnCss)
    .attr("for", "radio_" + area.id + "_" + SEVERITY_EXTENSIVE)
    .appendTo(radioGroup)
    .text("Extensive");
  extensiveItemLabel.on("click", function () {
    onItemClicked(SEVERITY_EXTENSIVE);
  });
  extensiveItemRadio.prop("checked", impactLevel == SEVERITY_EXTENSIVE);

  var deleteItemRadio = $('<input type="radio"/>')
    .addClass("btn-check")
    .attr("name", "radio_" + area.id)
    .attr("id", "radio_" + area.id + "_" + SEVERITY_NONE)
    .appendTo(radioGroup);
  var deleteItemLabel = $("<label/>")
    .addClass(btnCss)
    .attr("for", "radio_" + area.id + "_" + SEVERITY_NONE)
    .appendTo(radioGroup)
    .append($("<i/>").addClass("fa fa-times text-danger"));

  deleteItemLabel.on("click", function () {
    onItemClicked(SEVERITY_NONE);
  });

  var impactsBtns = $("#selectedDamages");

  function removeImpact() {
    var impactBtn = impactsBtns.find('*[data-areakey="' + area.id + '"]');
    imageArea.hide();
    imageCircle
      .find("div")
      .removeClass("impacts-image-inner-circle")
      .addClass("impacts-image-inner-plus");

    if (impactBtn.length > 0) impactBtn.remove();
    updateEstimateDamageBtn();
  }

  function updateEstimateDamageBtn() {
    var disabled = impactsBtns.find('[id^="impact_"]').length == 0;
    $("#add-estimate-damage-btn").prop("disabled", disabled);
  }

  function addImpact(impactLevel) {
    var impactBtn = impactsBtns.find('*[data-areakey="' + area.id + '"]');
    if (impactBtn.length > 0) impactBtn.remove();

    imageArea.show();
    imageCircle
      .find("div")
      .removeClass("impacts-image-inner-plus")
      .addClass("impacts-image-inner-circle");

    var desc = getAreaDesc(area.id) + " - " + getLevelDesc(impactLevel);
    var id = "impact_" + area.id + "_" + impactLevel;

    impactBtn = $('<button type="button" />')
      .addClass("btn btn-sm btn-warning impact-group")
      .attr("id", id)
      .text(desc)
      .attr("data-areakey", area.id)
      .attr("data-levelkey", impactLevel)
      .append(
        $("<span />")
          .addClass("close float-end remove-impact-x")
          .html("&nbsp;&times;")
          .css({ color: "#000000" })
      )
      .on(
        "click",
        (function (_areaId, _levelId) {
          return function (e) {
            onItemClicked(SEVERITY_NONE);
            e.preventDefault();
            return false;
          };
        })(area.id, impactLevel)
      )
      .on("mouseenter", function () {
        $(this)
          .find(".remove-impact-x")
          .css({ filter: "alpha(opacity = 50)", opacity: ".5" });
      })
      .on("mouseleave", function () {
        $(this)
          .find(".remove-impact-x")
          .css({ filter: "alpha(opacity = 20)", opacity: ".2" });
      });
    impactsBtns.append(impactBtn);
    updateEstimateDamageBtn();
  }

  function onItemClicked(impactLevel, hideRadio = true) {
    imageCircle
      .removeClass("slight")
      .removeClass("medium")
      .removeClass("extensive")
      .removeClass("empty");
    var circleColor = "";
    var hasImpact = impactLevel != SEVERITY_NONE;
    if (hasImpact) {
      addImpact(impactLevel);
    } else {
      removeImpact();
    }

    switch (impactLevel) {
      case SEVERITY_SLIGHT:
        circleColor = "slight";
        slightItemRadio.prop("checked", true);
        break;
      case SEVERITY_MEDIUM:
        circleColor = "medium";
        break;
      case SEVERITY_EXTENSIVE:
        circleColor = "extensive";
        break;
      case SEVERITY_NONE:
        circleColor = "empty";
        imageArea.hide();
        break;
    }
    imageCircle.addClass(circleColor);
    $(document).off("click.handleImpactLevelRadioOutsideClick");
    if (hideRadio) imageCircle.tooltip("hide");
  }

  return {
    radioGroup,
    onItemClicked,
  };
}

function hideAllImpactLevelRadio() {
  $(".impacts-image-circle").tooltip("hide");
}

function openImpactLevelRadio(e, imageCircle, menu) {
  hideAllImpactLevelRadio();
  imageCircle.tooltip("show");

  setTimeout(function () {
    $(document).on("click.handleImpactLevelRadioOutsideClick", function (e) {
      handleOutsideClick(e, imageCircle, menu);
    });
  }, 100);
}

function handleOutsideClick(event, imageCircle, popup) {
  if (!popup.is(event.target) && popup.has(event.target).length === 0) {
    imageCircle.tooltip("hide");
    $(document).off("click.handleImpactLevelRadioOutsideClick");
  }
}

function createImpactImage(container) {
  $.each(impactAreasTable, function (i, area) {

    var imageArea = $("<img/>")
      .attr("id", "impactsImageMap" + (i + 1))
      .attr("src", '/images/' + area.id + ".png")
      .attr("alt", "")
      .addClass("impacts-image impacts-image-area")
      .appendTo(container);
    var selectedLevel = null;
    var circleColor = "empty";
    var innerCssClass = "impacts-image-inner-plus";
    imageArea.css("display", "none");

    var imageCircle = $("<div />")
      .addClass("impacts-image-circle")
      .css({ top: area.y, left: area.x })
      .appendTo(container);

    var imageCircleEvent = function (e) {
      if ($(this).hasClass("empty")) addEmptyImpactFunc();
      openImpactLevelRadio(e, imageCircle, levelRadio);
    };

    imageCircle.on("click", imageCircleEvent);

    imageCircle.addClass(circleColor);
    imageCircle.append($("<div />").addClass(innerCssClass));

    var radioGroupProps = createImpactLevelRadio(
      selectedLevel,
      area,
      imageArea,
      imageCircle
    );
    var levelRadio = radioGroupProps.radioGroup;
    imageCircle.tooltip({
      sanitize: false,
      html: true,
      title: levelRadio,
      trigger: "manual",
      template:
        '<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner tooltip-inner-auto-width"></div></div>',
    });
    var addEmptyImpactFunc = function () {
      radioGroupProps.onItemClicked(SEVERITY_SLIGHT, false);
    };
  });

  $("#add-estimate-damage-btn").prop("disabled", true).on('click', function (e) {
    submitImpactsEstimate(e, $(this));
  });
}

async function submitImpactsEstimate(event, sender) {
  var damageAreas = []; // list of selected areas (areas[{area, severity}])
  var impactsBtns = $("#selectedDamages");
  impactsBtns.find('[id^="impact_"]').each(function () {
    var severity = $(this).data('levelkey');
    var area = $(this).data('areakey');
    damageAreas.push({ severity, area });
  });

  if (damageAreas.length > 0) {
    const result = await apiCallAsync('POST', `damages/${sessionTokenId}`, { damageAreas }, null, null, $('#add-estimate-damage-btn'));
    showTokenResult(result)
  }
}

async function initToken() {
  const params = new URLSearchParams(window.location.search);
  sessionTokenId = params.get("token");
  return await apiCallAsync('GET', `damages/${sessionTokenId}`);
}

function showTokenData(data) {
  const { claimNumber, insured, vehicle } = data;

  let html = `
        <div class="d-flex justify-content-around">
            <div class="d-flex flex-column align-items-start gap-2">
              <div><strong>Insured:</strong> ${insured.name}</div>
              <div><strong>Vehicle:</strong> ${vehicle.model} (${vehicle.year})</div>
            </div>
            <div class="d-flex flex-column align-items-start gap-2">
              <div><strong>Plate:</strong> ${vehicle.plateNumber}</div>
              <div><strong>claim:</strong> ${claimNumber}</div>
            </div>
        </div>
    `;
  $('#tokenInfo').html(html);
}

function showTokenResult(data) {
  const { claimNumber, status } = data;
  if (status == CLAIM_STATUS_APPROVED) {
    $('#tokenInfo').removeClass('alert-info').addClass('alert-success')
    let html = `
        <div>
            <h5><i class="fa-solid fa-thumbs-up"></i> Your claim #${claimNumber} is approved!</h5>
            <p>Thank you for your cooperation.</p>
        </div>
    `;
    $('#tokenInfo').html(html);

  }
  else {
    let html = `
        <div>
            <h5><i class="fa-solid fa-thumbs-down"></i> Your claim #${claimNumber} is not approved!</h5>
            <p>Thank you for your cooperation.</p>
        </div>
    `;
    $('#tokenInfo').html(html);

  }

  $(".impacts-image-container").hide();
  $('.selected-damages').hide();
  $('.bottom-bar').hide();
  $('.instractions-text').hide();
}

function showTokenError(errorMessage) {
  $('#tokenInfo').removeClass('alert-info').addClass('alert-danger')

  let html = `
        <div>
            <h5><i class="fa-solid fa-circle-exclamation"></i> Error loading token data!</h5>
            <p>${errorMessage}</p>
        </div>
    `;
  $('#tokenInfo').html(html);


  $(".impacts-image-container").hide();
  $('.selected-damages').hide();
  $('.bottom-bar').hide();
  $('.instractions-text').hide();


}




