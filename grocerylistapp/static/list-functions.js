

function clean_line(jsonData, place_to_append){

    console.log(place_to_append)
    place_to_append.children('.recipe-info, .button-panel').hide()

    var compiled_list = $('#compiled-list')
    place_to_append.append("<div id='clean-line' class='btn-group'></div>")

    var clean_line = $("#clean-line")

    var word_buttons = []
    for (var i in jsonData['parsed_line']){
      clean_line.append("<button class='" + jsonData['parsed_line'][i][1] + " word-button'>" + jsonData['parsed_line'][i][0] + "</button>")
    }

    $("#add-line-submit").toggleClass("hidden")
    $("#add-line-input").toggleClass("hidden")

    clean_line.append("<div id='commit-new-line' class='button-panel recipe-div'></div>")

    $("#commit-new-line").append("<button id='commit-button' class='edit-button'>Commit</button>")

    $("#commit-button").on('click', function(){
      window.location.href=$SCRIPT_ROOT + '/list/' + $LIST_HEX
    })

    // TODO: refactor so there isn't reused javascript like this
    var b_dict = {
      'btn-base': 'btn-ingredient',
      'btn-ingredient': 'btn-measurement',
      'btn-measurement': 'btn-amount',
      'btn-amount': 'btn-base',
    }
    var patt = /btn-[\w]+/  // regex pattern to find button class

    $('.word-button').click(function(){
      var btn_class = $( this ).attr("class").match(patt)[0]

      $( this ).toggleClass(btn_class)
      $( this ).toggleClass(b_simplified[btn_class])

    var children = clean_line.children('.word-button')

    var button_colors = []

    for (var i = 0; i < children.length; i++){
      button_text = $(children[i]).text()
      button_color = $(children[i]).attr('class').match(patt)[0]
      button_colors.push([button_text, button_color])
    }

    console.log(jsonData)

    var data = {
      'hex_id': jsonData['hex_id'],
      'text_to_colors': JSON.stringify(button_colors),
    }

    $.ajax({
      type: 'POST',
      url: $SCRIPT_ROOT + "/line/set_color",
      data: data,
      dataType: 'json',
      success: function(jsonData){
        console.log('ajax successful!')
      }
    })
  })

}

$(document).ready(function(){
  function link_dots(){
    if(!$( this ).hasClass("active")){
      var dot = $( this ).find("span")
      var color = dot.css("background-color")
      dot.toggleClass("d-none")

      var dots_to_hide = $("#compiled-list").find("span").filter(function(){
        return ($( this ).css("background-color") === color
          &&
          $( this ).hasClass("top-level"))
      })
      dots_to_hide.toggleClass("d-none")
  }
}

  function cross_out(){
    var checked_lines = $('.recipe-label').find('input:checked').each(function(index){
      var this_id = $( this ).attr('id').slice(9, 20)
      var line_to_cross = $('#line-' + this_id)
      line_to_cross.addClass('strikethrough')

    })
  }

  cross_out()

  var recipe_buttons = $('.recipe-button')

  recipe_buttons.hover(link_dots, link_dots)
  recipe_buttons.click(function(){
    $( this ).toggleClass("active")
  })


  $("#add-line-submit").on("click", function (){
    var new_line = $("#add-line-input").val()

    var list = $('#compiled-list')

    var data = {
      'line_text': new_line,
      'compiled_list': $LIST_HEX
    }

    // ajax call to parse the recipe line

    $.ajax({
      type: 'POST',
      url: $SCRIPT_ROOT + '/line/parse_line',
      data: data,
      dataType: 'json',
      success: function(jsonData){clean_line(jsonData, list)},
    })

    console.log(new_line)

  })

  $('.edit-button').on("click", function () {

    var line = $( this ).parents(".list-flex")
    console.log(line)
    var line_text = line.find('.recipe-line').text()
    console.log(line_text)


    var data = {
      'hex_id': line.attr('id')
    }

    console.log(data)

    $.ajax({
      type: 'POST',
      url: $SCRIPT_ROOT + '/line/get_colors',
      data: data,
      dataType: 'json',
      success: function(jsonData){
        console.log('success!')
        console.log(jsonData)
        clean_line(jsonData, line)
      }
    })
  })

  $('.edit-label').focusout(change_recipe_name)

  $('#rename-list-button').on("click", function(){
    var complist_div = $("#complist-name-div")
    var list_name = $("#complist-name").text()
    $("#complist-name").toggleClass("hidden")
    $( this ).toggleClass("hidden")
    $("<input id='change-name-input' class='name-input'></input>").prependTo(complist_div).val(list_name)
    $("<button id='confirm-name-button' class='btn btn-secondary'>Confirm</button>").appendTo(complist_div).on("click", function(){
      var new_name = $("#change-name-input").val()
      $.ajax({
        type:'POST',
        url: $SCRIPT_ROOT + '/list/rename',
        data: { 'name': new_name,
                'list': $LIST_HEX,
              },
        dataType: 'json',
        success: function(jsonData){
          $("#change-name-input").remove()
          $("#confirm-name-button" ).remove()
          $("#complist-name").text(jsonData['name']).toggleClass("hidden")
          $("#rename-list-button").toggleClass("hidden")

          $("#link-"+$LIST_HEX).text(jsonData['name'] + ' (' + $LIST_HEX + ')')

        }
      })
    })
  })

  $('.recipe-label').find('input').on("change", function(){
    var selected_line = $( this ).attr('id')
    data = {'line': selected_line.slice(9, 20)}

    $.ajax({
      type: 'POST',
      url: $SCRIPT_ROOT + '/line/checked',
      data: data,
      dataType: 'json',
      success: function(jsonData){
        console.log('line activation set to ' + jsonData['isActive'])
        $('#line-' + jsonData['line']).toggleClass('strikethrough')
      }
    })
  })

  $('.remove-button').on('click', function(){
    var del = confirm("Are you sure you want to delete this line?")
    if (del==true){
      var line_to_delete = $( this ).attr('id').slice(7, 18)
      console.log(line_to_delete)
      data = {"line": line_to_delete}
      $.ajax({
        type: 'POST',
        url: $SCRIPT_ROOT + "/line/delete",
        data: data,
        dataType: 'json',
        success: function(jsonData){
          var deleted_line = jsonData["line"]
          console.log("deleted " + deleted_line)
          $("#line-" + deleted_line).remove()
          $("#checkbox-" + deleted_line).parent().remove()

        }
      })
    }
  })

  function handle_mousedown(e){
    e.preventDefault()  // necessary to prevent the anchor from activating
    console.log("mouse down")

    var dragged_line = $( this ).parents('.full-line')
    dragged_line.css('z-index', '5')

    var list_positions = {}



    console.log(list_positions)

    window.my_dragging = {};
    my_dragging.pageX0 = e.pageX
    my_dragging.pageY0 = e.pageY
    my_dragging.elem = dragged_line
    my_dragging.offset0 = dragged_line.offset()

    function handle_dragging(e){
      e.preventDefault()
      var left = my_dragging.offset0.left + (e.pageX - my_dragging.pageX0)
      var top = my_dragging.offset0.top + (e.pageY - my_dragging.pageY0)
      $(my_dragging.elem).offset({top: top, left: left})
    }
    function handle_mouseup(e){
      e.preventDefault()
      console.log("mouse up")

      var all_lines = $('.full-line').not(dragged_line)

      console.log(all_lines)
      console.log(all_lines[0])

      var found = false
      for(var i = 0; i < all_lines.length-1; i++){
        if(found) break  // determines if we've found the point of insertion
        var current_line = all_lines[i]

        console.log($(all_lines[i]).offset())
        console.log(dragged_line.offset().top)
        console.log($(all_lines[i+1]).offset().top)
        if($(all_lines[i]).offset().top < dragged_line.offset().top
          && $(all_lines[i+1]).offset().top > dragged_line.offset().top){
            dragged_line.insertAfter($(all_lines[i]))
            found = true
          }
        }

      dragged_line.removeAttr('style')

      // send ajax request to reorder the list
      var line_list = {}
      $('.full-line').each(function(index){
        console.log($(this))
        line_list[$(this).attr('id').slice(5,16)] = index
      })

      console.log(line_list)


      $.ajax({
        type: 'POST',
        url: $SCRIPT_ROOT + '/list/reorder',
        data: {
          'list': $LIST_HEX,
          'order': JSON.stringify(line_list)
        },
        dataType: 'json',
        success: function(jsonData){
          console.log('list reordered')
        }
      })

      $('body')
      .off('mousemove', handle_dragging)
      .off('mouseup', handle_mouseup);
    }
    $('body')
    .on('mouseup', handle_mouseup)
    .on('mousemove', handle_dragging);
  }

  $('.drag-button').mousedown(handle_mousedown)


})
