$(document).ready(function() {

  /*
  // All forms should take the CSRF token and make it set it as a hidden
  // input on all forms.
  (function() {
    $('form').append($('<input>').attr({
      type: 'hidden',
      name: csrf_key,
      value: csrf_token
    }));
  })();
  */

  // The #payment-form should use Stripe
  // We assume the Stripe <script> tag is included in the template
  (function() {
    $('form#funding-source').submit(function(e) {
      // Set our non-private key so that Stripe knows who we are
      // Test key:
      Stripe.setPublishableKey('');
      // Prod key:
      // Stripe.setPublishableKey('');

      // Disable the submit button to prevent duplicate submits...
      $(this).find('button').attr('disabled', 'disabled');

      // Send a request to create a token, trigger the callback above
      Stripe.createToken({
        number: $(this).find('#card_number').val(),
        cvc: $(this).find('#card_cvc').val(),
        exp_month: $(this).find('#card_exp_month').val(),
        exp_year: $(this).find('#card_exp_year').val()
      }, stripeResponseHandler);

      // Don't actually submit the form.
      return false;
    });

    // What happens when we hear back from Stripe
    var stripeResponseHandler = function(status, response) {
      var $form = $('form#credit-card');

      if (response.error) {
        // Hide and remove all previous error tooltips
        $form.find('input').each(function() {
          var tooltip = $(this).data('tooltip');
          if (tooltip) {
            tooltip.$tip.hide();
          }
        });
        $form.find('input').removeData('tooltip');

        // Re-enable the button so that we can try again
        $form.find('button').removeAttr('disabled');
        $form.find('button').data('spinner-reset')();

        // Show that errors happened...
        var $field = $form.find('#card_' + response.error.param);
        $field.tooltip({
          title: response.error.message
          // trigger: 'manual' keeps the tooltip visible (and covering up
          // other fields). Let's leave this out for now.
        }).tooltip('show');
      } else {
        // Append relevate data as a hidden input to the form
        $('<input>').attr({
          type: 'hidden',
          name: 'card_token',
          value: response['id']
        }).appendTo($form);

        // We don't want the card cvc
        $form.find('#card_cvc').remove();

        // We only want the last four digits:
        $form.find('#card_number').val(response['card']['last4']);

        // Change the name of that field before submitting
        $form.find('#card_number').attr('name', 'card_last_four_digits');

        // And submit the HTMLElement form (not the jQuery form...)
        $form.get(0).submit();
      }
    };
  })();

  // When the button with data-spinner is clicked, it should become a spinner
  (function() {
    $('button[data-spinner]').each(function() {
      var $button = $(this);

      $button.data('spinner-show', function() {
        // If we're showing for the first time (no progress bar created yet).
        if (!$button.data('spinner-element')) {
          var height = ($button.outerHeight() - 2) + 'px';
          var width = $button.outerWidth() + 'px';
          var $progress = $('<div>').addClass('progress progress-striped active').css({
            cursor: 'pointer',
            display: $button.css('display'),
            float: $button.css('float'),
            marginBottom: 0,
            border: '1px solid #666',
            height: height,
            width: width
          });
          var $bar = $('<div>').addClass('bar').css({
            height: height,
            width: width,
            lineHeight: height,
            fontSize: '13px',
            fontWeight: 'bold'
          }).html($button.data('spinner'));

          $bar.appendTo($progress);
          $progress.insertAfter($button).hide();
          $button.data('spinner-element', $progress);
        }

        $button.data('spinner-element').show();
        $button.hide();
      });

      $button.data('spinner-reset', function() {
        $button.data('spinner-element').hide();
        $button.show();
      });

      if ($button.parents('form').length) {
        $button.parents('form').submit($button.data('spinner-show'));
      }
      else {
        $button.click($button.data('spinner-show'));
      }
    });
  })();

  // Auto generated function from http://toolki.com/en/google-maps,
  // for roadmap on contact page.
  (function() {
    // If we don't have the "google" variable, don't run this method.
    if (typeof google === 'undefined') return;

    var myLatlng = new google.maps.LatLng(18.007450,-76.7477990);
    var myOptions = {
        zoom: 15,
        center: myLatlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP}

    var map = new google.maps.Map(document.getElementById("map-canvas"), myOptions);

    var contentString = "";

    var infowindow = new google.maps.InfoWindow({
        content: contentString
    });

    var marker = new google.maps.Marker({
        position: myLatlng,
        map: map,
        title: ""
    });
    google.maps.visualRefresh=true
    google.maps.event.addListener(marker, 'click', function() {
        infowindow.open(map,marker);
    });
  })();


  // Use data-modal to show the nearest modal matching the selector
  (function() {
    $('[data-modal]').removeAttr('href').click(function() {
      var selector = '.modal.' + $(this).data('modal');
      var $modal = $(this).closest(':has(' + selector + ')').find(selector);
      $modal.modal();
    });
  })();

  // .dropdown-timepicker's should act like timepicker objects.
  (function() {
    $('.dropdown-timepicker').timepicker({
      minuteStep: 30,
      disableFocus: false
    });
  })();

  // .datepicker's should act like datepicker objects.
  (function() {
    $('.datepicker').datepicker({
      autoclose: true
    });
  })();

  // .nav-tabs should act as tabs
  (function() {
    $('.nav-tabs a').click(function(e) {
      e.preventDefault();
      $(this).tab('show');
    });
  })();

  // Use rel=tooltip to designate that we want a tooltip.
  (function() {
    $(document).tooltip({
      selector: '[rel=tooltip]'
    });
  })();

  // #notification-bar should fade away after 10 seconds.
  (function() {
    setTimeout(function() {
      $('#notification-bar').fadeOut('slow');
    }, 10000);
  })();

  // .nav-tabs should automatically select the first tab if we provide
  // data-select-first in the definition.
  (function() {
    $('.nav-tabs[data-select-first] li:first a:first').click();
  })();

  // Sign in button on homepage
  (function() {
    $('#login-button').click(function(e){
      $(this).toggleClass('login-active');
      $('#login-form').toggle();
      return false;
    });
  })();

});
