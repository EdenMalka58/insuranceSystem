
var sessionTokenId = null;

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

function createImpactLevelRadio(impactLevel, area, imageArea, imageCircle) {
  const radioGroup = $('<div />').addClass('btn-group').attr('role', 'group');
  const btnCss = 'btn btn-outline-primary btn-sm';
  const impactsBtns = $('#selectedDamages');
  const radios = {}; // Store radio references

  // Create radio buttons dynamically
  SEVERITY_LEVELS.forEach(level => {
    const radioId = `radio_${area.id}_${level.value}`;

    const radio = $('<input type="radio"/>')
      .addClass('btn-check')
      .attr({ name: `radio_${area.id}`, id: radioId })
      .prop('checked', impactLevel === level.value)
      .appendTo(radioGroup);

    radios[level.value] = radio; // Store reference

    const label = $('<label/>')
      .addClass(btnCss)
      .attr('for', radioId)
      .appendTo(radioGroup);

    level.isDelete ? label.append($(level.label)) : label.text(level.label);

    label.on('click', () => onItemClicked(level.value));
  });

  function updateEstimateDamageBtn() {
    const hasImpacts = impactsBtns.find('[id^="impact_"]').length > 0;
    $('#add-estimate-damage-btn').prop('disabled', !hasImpacts);
  }

  function removeImpact() {
    impactsBtns.find(`[data-areakey="${area.id}"]`).remove();
    imageArea.hide();
    imageCircle.find('div')
      .removeClass('impacts-image-inner-circle')
      .addClass('impacts-image-inner-plus');
    updateEstimateDamageBtn();
  }

  function addImpact(impactLevel) {
    // Remove existing impact for this area
    impactsBtns.find(`[data-areakey="${area.id}"]`).remove();

    imageArea.show();
    imageCircle.find('div')
      .removeClass('impacts-image-inner-plus')
      .addClass('impacts-image-inner-circle');

    const desc = `${getAreaDesc(area.id)} - ${getLevelDesc(impactLevel)}`;
    const id = `impact_${area.id}_${impactLevel}`;

    const impactBtn = $('<button type="button" />')
      .addClass('btn btn-sm btn-warning impact-group')
      .attr({ id, 'data-areakey': area.id, 'data-levelkey': impactLevel })
      .text(desc)
      .append(
        $('<span />')
          .addClass('close float-end remove-impact-x')
          .html('&nbsp;&times;')
          .css({ color: '#000000', filter: 'alpha(opacity=20)', opacity: '.2' })
      )
      .on('click', (e) => {
        onItemClicked(SEVERITY_NONE);
        e.preventDefault();
        return false;
      })
      .on('mouseenter', function () {
        $(this).find('.remove-impact-x').css({ filter: 'alpha(opacity=50)', opacity: '.5' });
      })
      .on('mouseleave', function () {
        $(this).find('.remove-impact-x').css({ filter: 'alpha(opacity=20)', opacity: '.2' });
      });

    impactsBtns.append(impactBtn);
    updateEstimateDamageBtn();
  }

  function onItemClicked(impactLevel, hideRadio = true) {
    const severityClasses = ['slight', 'medium', 'extensive', 'empty'];
    imageCircle.removeClass(severityClasses.join(' '));

    if (impactLevel !== SEVERITY_NONE) {
      addImpact(impactLevel);
    } else {
      removeImpact();
    }

    // Map severity to CSS class
    const classMap = {
      [SEVERITY_SLIGHT]: 'slight',
      [SEVERITY_MEDIUM]: 'medium',
      [SEVERITY_EXTENSIVE]: 'extensive',
      [SEVERITY_NONE]: 'empty'
    };

    imageCircle.addClass(classMap[impactLevel] || 'empty');

    // Update the corresponding radio button using stored reference
    if (radios[impactLevel]) {
      radios[impactLevel].prop('checked', true);
    }

    if (impactLevel === SEVERITY_NONE) {
      imageArea.hide();
    }

    $(document).off('click.handleImpactLevelRadioOutsideClick');
    if (hideRadio) imageCircle.tooltip('hide');
  }

  return { radioGroup, onItemClicked };
}

function hideAllImpactLevelRadio() {
  $('.impacts-image-circle').tooltip('hide');
}

function openImpactLevelRadio(e, imageCircle, menu) {
  hideAllImpactLevelRadio();
  imageCircle.tooltip('show');

  setTimeout(() => {
    $(document).on('click.handleImpactLevelRadioOutsideClick', (e) => {
      if (!menu.is(e.target) && menu.has(e.target).length === 0) {
        imageCircle.tooltip('hide');
        $(document).off('click.handleImpactLevelRadioOutsideClick');
      }
    });
  }, 100);
}

function createImpactImage(container) {
  DAMAGE_AREAS.forEach((area, i) => {
    const imageArea = $('<img/>')
      .attr({
        id: `impactsImageMap${i + 1}`,
        src: `/images/${area.id}.png`,
        alt: ''
      })
      .addClass('impacts-image impacts-image-area')
      .css('display', 'none')
      .appendTo(container);

    const imageCircle = $('<div />')
      .addClass('impacts-image-circle empty')
      .css({ top: area.y, left: area.x })
      .append($('<div />').addClass('impacts-image-inner-plus'))
      .appendTo(container);

    const { radioGroup, onItemClicked } = createImpactLevelRadio(
      null,
      area,
      imageArea,
      imageCircle
    );

    imageCircle.on('click', (e) => {
      if (imageCircle.hasClass('empty')) {
        onItemClicked(SEVERITY_SLIGHT, false);
      }
      openImpactLevelRadio(e, imageCircle, radioGroup);
    });

    imageCircle.tooltip({
      sanitize: false,
      html: true,
      title: radioGroup,
      trigger: 'manual',
      template: '<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner tooltip-inner-auto-width"></div></div>'
    });
  });

  $('#add-estimate-damage-btn')
    .prop('disabled', true)
    .on('click', submitImpactsEstimate);
}

async function submitImpactsEstimate(event) {
  const damageAreas = $('#selectedDamages')
    .find('[id^="impact_"]')
    .map(function () {
      return {
        severity: $(this).data('levelkey'),
        area: $(this).data('areakey')
      };
    })
    .get();

  if (damageAreas.length > 0) {
    const result = await apiCallAsync(
      'POST',
      `damages/${sessionTokenId}`,
      { damageAreas },
      null,
      null,
      $('#add-estimate-damage-btn')
    );
    showTokenResult(result);
  }
}

