$(function(){
  var word_buttons = $('.word-button')
  var hex_name = $('#hex-name').text()
  console.log(hex_name)

  var b_cycle = ['btn-base', 'btn-ingredient', 'btn-amount', 'btn-measurement']

  var b_dict = {
    'btn-base': 'btn-ingredient',
    'btn-ingredient': 'btn-measurement',
    'btn-measurement': 'btn-amount',
    'btn-amount': 'btn-base',
  }

  word_buttons.click(function(){

    var patt = /btn-[\w]+/  // regex pattern to find button class

    var btn_class = $( this ).attr("class").match(patt)[0]

    $( this ).toggleClass(btn_class)
    $( this ).toggleClass(b_dict[btn_class])



    var line = $( this ).parent()
    var line_id = line.attr('id')

    var children = line.children()

    var button_colors = []

    for (var i = 0; i < children.length; i++){
      button_text = $(children[i]).text()
      button_color = $(children[i]).attr('class').match(patt)[0]
      console.log(button_color)
      button_colors.push([button_text, button_color])
    }



    var data = {'hex_name': hex_name,
                'recipe_line': line_id,
                'text_to_colors': JSON.stringify(button_colors)}
    console.log(data)

    $.ajax({
      type: 'POST',
      url: $SCRIPT_ROOT + '/line/set_color',
      data: data,
      dataType: 'json',
      success: function(jsonData){
        console.log(jsonData)
      }
    })
  });
});
