

$(function(){
  var word_buttons = $('.word-button')

  var b_cycle = ['btn-base', 'btn-ingredient', 'btn-amount', 'btn-measurement']

  var b_dict = {
    'btn-base': 'btn-ingredient',
    'btn-ingredient': 'btn-measurement',
    'btn-measurement': 'btn-amount',
    'btn-amount': 'btn-base',
  }


  create_ingredient_groups()

  word_buttons.click(function(){

    var patt = /btn-[\w]+/  // regex pattern to find button class

    var btn_class = $( this ).attr("class").match(patt)[0]


    $( this ).toggleClass(btn_class)
    $( this ).toggleClass(b_simplified[btn_class])



    var line = $( this ).parents('.raw-line')
    var line_id = line.attr('id')

    var children = line.find('button') // don't get the empty divs
    console.log(children)

    var button_colors = []

    for (var i = 0; i < children.length; i++){
      button_text = $(children[i]).text()
      console.log(button_text)
      button_color = $(children[i]).attr('class').match(patt)[0]
      console.log(button_color)
      button_colors.push([button_text, button_color])
    }



    var data = {'hex_id': line_id,
                'text_to_colors': JSON.stringify(button_colors)}
    console.log(data)

    var button = $(this)

    $.ajax({
      type: 'POST',
      url: $SCRIPT_ROOT + '/line/set_color',
      data: data,
      dataType: 'json',
      success: function(jsonData){
        console.log(jsonData)
        update_ingredient_groups(button)
      }
    })
  });

  $('#recipe-title').click(function(){
    $(this).attr('spellcheck', 'true')
  })


  function change_recipe_name(){
    return change_name('recipe', $RECIPE_HEX, $(this).text())
  }

  $('#recipe-title').focusout(change_recipe_name)
  $('#recipe-title').keypress(function(event){
    if (event.keyCode == '13'){
      event.preventDefault()
      change_recipe_name()
      $( this ).blur()
    }
  })

  $('#submit-list').click(function(){
    // create a small form and submit with empty post data, cleaning lines
    // is handled server side
    var form = $("<form action='' method='post'></form>")
    $('body').append(form)
    form.submit()
  })


});
