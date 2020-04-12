function change_recipe_name(){
    $(this).attr('spellcheck', 'false')

    var data = {'recipe_id': $RECIPE_HEX,
                'name': $(this).text()}

    console.log(data)

    $.ajax({
      type: 'POST',
      url: $SCRIPT_ROOT + '/recipe/rename',
      data: data,
      dataType: 'json',
      success: function(jsonData){
        console.log('new name is ' + jsonData['new_name'])
      }
    })
}

var b_simplified = {
  'btn-ingredient': 'btn-base',
  'btn-base': 'btn-ingredient'
}

function change_name(){

}
