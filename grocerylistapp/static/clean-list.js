

$(function(){
  var selector = $("#ingredient-selector")
  var offset = selector.offset().top


  $( window ).scroll(function(){
    var win_offset = $( window ).scrollTop()

    if (win_offset >= offset){
      selector.addClass("sticky")
    } else {
      selector.removeClass("sticky")
    }

  })



  var word_buttons = $('.word-button')

  var b_cycle = ['btn-base', 'btn-ingredient', 'btn-amount', 'btn-measurement']

  var b_dict = {
    'btn-base': 'btn-ingredient',
    'btn-ingredient': 'btn-measurement',
    'btn-measurement': 'btn-amount',
    'btn-amount': 'btn-base',
  }

  var b_ings = ["ing-1", "ing-2", "ing-3"]

  $(".raw-line").each(function(){
    console.log($(this))
    create_ingredient_groups($(this))
  })


  var current_color = "ing-1"

  // get the current color we're painting with
  $("input[name='color']").click(function(){
    current_color = $("input[name='color']:checked").val()
    console.log(current_color)
  })


  word_buttons.click(function(){
    send_line_data($(this), current_color)
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
