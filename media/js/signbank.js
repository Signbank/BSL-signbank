$(document).ready(function() {
  // Registration form
  // On the registration form only show researcher credentials if we select
  // a background that includes the word research
  if ($('#id_researcher_credentials')) {
    $('#id_researcher_credentials').parent('div').hide();
    $('#id_background').on('change', function (e) {
      var selectedText = $("option:selected", $('#id_background')).text();
      if (selectedText.indexOf("research") > -1) {
        $('#id_researcher_credentials').parent('div').show();
      } else {
        $('#id_researcher_credentials').parent('div').hide();
      }
    });
  }



  // Sign feature search
  // Replace the dropdown list with an image map we can click to pick a handshape
  $("#handshape_dropdown").show();
  $("#id_handshape").hide();
  // Fill in the existing handshape for this search
  var existing = $("#id_handshape option:selected").text();
  if (existing == 'No Value Set') {
    existing = 'Any Handshape';
  }
  $('#dropdown_menu_handshape span.content').text(existing);
  // Copy the alt tag to title for a little label tooltip on compatible browsers
  // Also fill in the href with something meaningful
  $("#handshape-map area").each(function(event) {
    var pickAlt = $(this).prop('alt');
    $(this).prop('title', pickAlt);
    $(this).prop('href', '#handshape-' + pickAlt);
  });
  // When we click the image map fill the select value and display a meaningful value
  $("#handshape-map area").click(function(event) {
    event.preventDefault();
    var pickVal = $(this).data('pick');
    var pickAlt = $(this).prop('alt');
    if (pickVal == undefined) {
      pickVal = 'notset';
      pickAlt = 'Any Handshape';
    }
    $('#id_handshape').val(pickVal);
    $('#dropdown_menu_handshape span.content').text(pickAlt);
  });


  // Replace the dropdown list with an image map we can click to pick a location
  $("#location_dropdown").show();
  $("#id_location").hide();
  // Fill in the existing location for this search
  var existing = $("#id_location option:selected").text();
  if (existing == 'No Value Set') {
    existing = 'Any Location';
  }
  $('#dropdown_menu_location span.content').text(existing);
  // Copy the alt tag to title for a little label tooltip on compatible browsers
  // Also fill in the href with something meaningful
  $("#location-map area").each(function(event) {
    var pickAlt = $(this).prop('alt');
    $(this).prop('title', pickAlt);
    $(this).prop('href', '#location-' + pickAlt);
  });
  // When we click the image map fill the select value and display a meaningful value
  $("#location-map area").click(function(event) {
    event.preventDefault();
    var pickVal = $(this).data('pick');
    var pickAlt = $(this).prop('alt');
    if (pickVal == undefined) {
      pickVal = '-1';
      pickAlt = 'Any Location';
    }
    $('#id_location').val(pickVal);
    $('#dropdown_menu_location span.content').text(pickAlt);
  });
});
