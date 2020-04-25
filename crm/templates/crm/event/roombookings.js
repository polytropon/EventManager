{% load admin_urls %}
{# New room partner chosen from select list #}
function roomPartnerChange(event){
  select_element = event.srcElement;
  formentry_id = event.srcElement.value;
  // Gets activated menu
  activatedPartnerContainers = document.getElementsByClassName("menuActivated");
}

{# Type of room (DZ/EZ) is changed #}
function roomChange(event){
  var sel = event.srcElement;
  var formentry_id = sel.parentElement.dataset.pk;
  var room_partner_div = document.getElementById("room_partner"+formentry_id);
  var room_type = sel.options[sel.selectedIndex].text;
  if (room_type.includes("DZ")) {
    room_partner_div.removeAttribute("class");
  } else {
    room_partner_div.setAttribute("class","hide");
  }
  {# Save change to backed first, then get new statistics from backend #}
  save(event,callback=statistics);
}

{# Status is changed #}
function statusChange(event){
  {# Save change to backed first, then get new statistics from backend #}
  save(event,callback=statistics);
}

// Room partner menu is triggered
// TODO: Add (DZ) or remove (EZ, Extern) person from activated partner containers:
// activatedPartnerContainers = document.getElementsByClassName("menuActivated");
function roomPartner(event){
  var formentry_id = event.srcElement.dataset.pk;
  event.srcElement.removeAttribute("onclick");

  $.ajax(
    {
      url: '{% url 'crm:select_room_partner' %}' ,
      data: {"formentry_id":formentry_id},
      dataType: 'html',
      success: function (data) {
        container_tag = $("#roomPartner"+formentry_id);
        container_tag.html(data);
        container_tag.attr("class","menuActivated");
        
        // TODO: Check whether room partner is already allocated
        // var rooms = $("[data-column='Übernachtung'][data-startvalue='DZ']");
      }
    }
  )
}