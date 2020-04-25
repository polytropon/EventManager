{# Code required for floating table headers #}
var $table = $('#float_table');
var reinit = $table.floatThead('destroy');
$('#float_table').floatThead({
  position: 'auto'
});
