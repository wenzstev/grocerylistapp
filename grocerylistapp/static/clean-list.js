// link ingredients into a button-group

function create_ingredient_groups(){
  $(".raw-line").each(function(){  // iterate through each line
    button_group = "<div class='btn-group ingredient-group d-inline align-baseline'></div>"
    current_group = $(button_group) // create button group div
    current_line = $(this)
    $( this ).children().each(function(){
      var next = $(this).next()
      if ($( this ).hasClass('btn-ingredient')){
        $(this).appendTo(current_group)
        if (next.length == 0){
          current_line.append(current_group)
        }
      }
      else if (current_group.children().length > 0){
        // end of button group, insert into line
        console.log("time to insert")
        current_group.insertBefore($(this))
        current_group = $(button_group) // reset group
      }
    })
  });
}

function update_ingredient_groups(button){
  console.log(button.text())

  // check if button is in group
  if (button.parent().hasClass('btn-group')){
    console.log(button.text() + " is in a group")
    // if it's in a group, we need to remove it
    // if it is in the middle of the group, we need to split the group
    at_beginning = (button.prev().length==0)
    at_end = (button.next().length==0)

    console.log(at_beginning + " " + at_end)

    if (at_beginning){
      if (at_end){
        // one word group, just remove
        button.unwrap()
      }
      else {
        // drop from beginning
        console.log(button.parent().prev())
        button.insertAfter(button.parent().prev())
      }
    }
    else if (at_end){
      // drop from end
      button.insertBefore(button.parent().next())
    }
    else { // split the group
      // create new button group
      new_group = $(button_group) // create button group div

      // move the second half of the group into the second group
      new_group.append(button.nextAll())

      // move the button up one
      button.insertBefore(button.parent().next())

      // append group after button
      new_group.insertAfter(button)
    }

  }

  else { // button is not in a group
    group_before = button.prev().hasClass('btn-group')
    group_after = button.next().hasClass('btn-group')

    if (group_before){
      if (group_after){
        // combine the two groups
        // get the buttons in the next group
        group_to_combine = button.next().children()
        // get rid of the group around them
        group_to_combine.unwrap()
        // insert them into the group before
        group_to_combine.appendTo(button.prev())
        // insert the button into the group before them
        button.insertBefore(group_to_combine)

      }
      else {
        // insert button into the group before it
        button.appendTo(button.prev())
      }
    }
    else {
      if (group_after){
        // insert button into the group after it
        button.prependTo(button.next())
      }
      else {
        // create a new group
        button.wrap(button_group)
      }
    }

    console.log(group_before + "  " + group_after)
  }

}

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

  $('#recipe-title').focusout(change_recipe_name)
  $('#recipe-title').keypress(function(event){
    if (event.keycode = '13'){
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
