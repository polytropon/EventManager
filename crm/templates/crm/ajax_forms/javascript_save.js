{% include "crm/ajax_forms/csrf.js" %}

function save (event,callback=false) {
  var src = event.srcElement;
  var div = src.parentElement;
  console.log("save event.srcElement:");
  console.log(event.srcElement);

  console.log("div element:");
  console.log(div);

  if (src.getAttribute("type")  == "datetime-local") {
    var newvalue = src.value.replace("T"," ");
  } else if (src.getAttribute("type") == "checkbox") {
    var newvalue = src.checked;
  }
  else {
    var newvalue = src.value;
  }

  if (div.dataset.startvalue != newvalue) {
    
  $.ajax({
    type:"POST",
    url: '{% url 'crm:ajax_save' %}',
    data: {
      "newvalue":newvalue,
      "startvalue":div.dataset.startvalue,
      "pk":div.dataset.pk,
      "model":div.dataset.model,
      "column":div.dataset.column
    },
    dataType: 'json',
    success: function (data) {
      div.setAttribute("data-startvalue", newvalue);
      if(callback) {
        callback(event);
      }
    }
  }
  )
}

};