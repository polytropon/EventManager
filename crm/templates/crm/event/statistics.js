function statistics(){
    $.ajax({
      url: '{% url 'crm:seminar_statistics' event.pk %}',
      data: {},
      dataType: 'html',
      success: function (data) {
        $("#statistics").html(data);
      }
    });
  }
  
  $ ( document ).ready(statistics());