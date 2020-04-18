

function clean_line(jsonData, clean_line){

    clean_line.children().hide()
    clean_line.addClass('raw-line') // add the raw line class so that create_ingredient_groups can find it

    clean_line.append("<span></span>")

    var word_buttons = []
    for (var i in jsonData['parsed_line']){
      clean_line.append("<button class='" + jsonData['parsed_line'][i][1] + " word-button float-none'>" + jsonData['parsed_line'][i][0] + "</button>")
    }

    clean_line.append("<span></span>")

    create_ingredient_groups(clean_line)

    var patt = /btn-[\w]+/  // regex pattern to find button class

    $('.word-button').click(function(){
      var line_color = $( this ).parents(".full-line").attr("id").slice(17, 22) // gives us the color to use
      send_line_data($(this), line_color)

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

  $('.recipe-info').on("click", function () {

    var line = $( this )

    var data = {
      'hex_id': $( this ).attr('id')
    }


    $.ajax({
      type: 'POST',
      url: $SCRIPT_ROOT + '/line/get_colors',
      data: data,
      dataType: 'json',
      success: function(jsonData){
        clean_line(jsonData, line)
        line.prop("disabled", true)
      }
    })
  })

  function change_list_name(){
    return change_name('list', $LIST_HEX, $(this).text())
  }

  $('.edit-label').focusout(change_list_name)
  $('.edit-label').keypress(function(event){
    console.log(event)
    if (event.keyCode == '13'){
      event.preventDefault()
      change_list_name()
      $( this ).blur()
    }
  })

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
