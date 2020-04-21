
function change_name(type, id, new_name){
    $(this).attr('spellcheck', 'false')

    console.log(this)

    data = {'name': new_name,
            'id': id}



    console.log(data)

    $.ajax({
      type: 'POST',
      url: $SCRIPT_ROOT + '/' + type + '/rename',
      data: data,
      dataType: 'json',
      success: function(jsonData){
        console.log('new name is ' + jsonData['new_name'])
      }
    })
}

// link ingredients into a button-group
var button_group = "<div class='btn-group ingredient-group d-inline align-baseline float-none'></div>"
var ing_reg = /ing-[\d]/

function create_ingredient_groups(line) {
    current_group = $(button_group) // create button group div
    current_line = line
    var cur_group_color = ""
    line.children().each(function(){
      var next = $(this).next()
      if ($( this ).hasClass('btn-ingredient')){
        var button_reg = $( this ).attr("class").match(ing_reg)
        if(button_reg != null){
          var button_color = button_reg[0]
          if (button_color == cur_group_color) {
            // still in same group
            $(this).appendTo(current_group)
          } else {
              if (current_group.children().length > 0){
                // new button group, insert old and reset
                current_group.insertBefore($(this))
                cur_group_color = button_color
                current_group = $(button_group)
                current_group.append($(this))
              } else {
                // first button of new group
                current_group.append($(this))
                cur_group_color = button_color
              }
          }
        }

        if (next.length == 0){ // end of line
          current_line.append(current_group)
        }
      }
      else if (current_group.children().length > 0){
        // end of button group, insert into line
        current_group.insertBefore($(this))
        current_group = $(button_group) // reset group
      }
    })
}

function strip_groups(line){
  console.log(line)
  line.children(".btn-group").each(function(){
    $(this).children().unwrap()
  })
}

function send_line_data(button, current_color){
  var patt = /btn-[\w]+/  // regex pattern to find button class

  var btn_class = button.attr("class").match(patt)[0]

  var ing = /ing-[\d]/
  var button_reg = button.attr("class").match(ing)

  if (button_reg != null){
    if (button_reg[0] == current_color){
      // toggle out of group
      button.toggleClass(button_reg[0])
      button.toggleClass(btn_class)
      button.toggleClass(b_simplified[btn_class])
    } else {
      // toggle into new group
      button.addClass(current_color)
      button.removeClass(button_reg[0])
    }
  } else {
    button.addClass(current_color)
    button.toggleClass(btn_class)
    button.toggleClass(b_simplified[btn_class])
  }


  var line = button.parents('.raw-line')
  var line_id = line.attr('id')

  var children = line.find('button') // don't get the empty divs

  var button_colors = []

  for (var i = 0; i < children.length; i++){
    button_text = $(children[i]).text()
    var child_ingredient_reg = $( children[i] ).attr("class").match(ing)
    var button_ingredient = ""
    if (child_ingredient_reg != null){
      button_ingredient = " " + child_ingredient_reg[0]
    }

    button_color = $(children[i]).attr('class').match(patt)[0] + button_ingredient

    button_colors.push([button_text, button_color])
  }



  var data = {'rawline_id': line_id,
              'text_to_colors': JSON.stringify(button_colors)}

  if (typeof $LIST_HEX !== 'undefined'){
    // we're on a list page
    data['list_id'] = $LIST_HEX
  }

  // check if we have a cleaned line and if so add it
  line_id = $( button ).parents('.full-line').attr('id')
  if (line_id != null){
    console.log(line_id.slice(5, 16))
    data['cleanedline_id'] = line_id.slice(5, 16)
  }
  console.log(line_id)

  $.ajax({
    type: 'POST',
    url: $SCRIPT_ROOT + '/line/set_color',
    data: data,
    dataType: 'json',
    success: function(jsonData){
      strip_groups(line)
      create_ingredient_groups(line)
      console.log(jsonData)
      var type = jsonData["type"]
      if (type == "changed") {
        // change existing line
        console.log(jsonData["change"])
        for (var line_index in jsonData["change"]){
          current_line = jsonData["change"][line_index]
          console.log(current_line[0] + " " + current_line[1])
          $("#line-" + current_line[0]).find(".ingredient-name").text(current_line[1])
        }
      } else if (type == "moved"){
        // moving raw line to a new cleaned line
        console.log("moving raw line")
        console.log(jsonData["change"])
        for (var line_index in jsonData["change"]){
          lines_to_change = jsonData["change"][line_index]
          console.log(lines_to_change)
          rawline_clicked_on = $("#" + lines_to_change[0])
          cleanedline_clicked_on = rawline_clicked_on.parents('.full-line')
          line_to_move = $("#line-" + lines_to_change[1])

          // 1. move the rawline div to the new parent
          rawline_clicked_on.prependTo(line_to_move.children('.collapse'))
          line_to_move.children('.collapse').addClass('show')

          // 2. insert the new parent into where the old cleanedline was
          cleanedline_clicked_on.after(line_to_move.parent())

        }
      } else if (type == "create"){
        // creating a new cleaned line
        console.log("creating new line")
        console.log(jsonData["change"])
        for (var index in jsonData["change"]){
          lines_to_change = jsonData["change"][index]
          rawline_clicked_on = $("#" + lines_to_change[0])
          cleanedline_to_create = lines_to_change[1]
          // new ajax request to get the html for the new line
          $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/line/build',
            data: {'line': cleanedline_to_create},
            dataType: 'html',
            success: function(htmlData){
              new_line = $(htmlData)
              console.log(new_line)
              new_line.find('.remove-button').on('click', delete_line)
              new_line.find('.recipe-info').on('click', get_line_data)
              new_line.find('input').on("change", cross_out_line)

              new_line.insertBefore(rawline_clicked_on.parents('.full-line'))
              new_line.find('.recipe-info').replaceWith(rawline_clicked_on)
            }
          })
        }
      }

      // check for divs to delete
      if (jsonData["delete"] !== 'undefined'){
        console.log("need to delete")
        line_to_delete = $("#line-" + jsonData["delete"]).parent()
        line_to_delete.remove()
      }
    }
  })
}

// currently unused
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


var b_simplified = {
  'btn-ingredient': 'btn-base',
  'btn-base': 'btn-ingredient'
}
