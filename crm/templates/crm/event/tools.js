{# Use views.send_answers_participation to send emails to participants #}
    function sendAnswersParticipation() {
      $.ajax({
        url: '{% url 'crm:send_answers_participation' event.pk %}',
        data: {},
        dataType: 'json',
        success: function (data) {
          location.reload(true);
        }
      });
    }

function toggleTrash() {
    if ($("#toggleTrash").html() == "Papierkorb anzeigen" ) {
        $("#toggleTrash").html("Papierkorb verstecken");
        $(".trash").removeClass("hide");
    } else {
        $("#toggleTrash").html("Papierkorb anzeigen");
        $(".trash").addClass("hide");
    }
    
    }