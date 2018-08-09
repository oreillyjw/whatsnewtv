var notifications_template = Handlebars.compile(document.querySelector('#notifications-template').innerHTML);

// value comaprision in handlebars in the template
// https://gist.github.com/pheuter/3515945
Handlebars.registerHelper("ifvalue", function(conditional, options) {
    if (conditional == options.hash.equals) {
        return options.fn(this);
    } else {
        return options.inverse(this);
    }
});

var searchHovered = false;

$(".navbar-nav > form > button").bind("mouseover",function() {
    searchHovered = true;
}).bind("mouseout",function() {
    searchHovered = false;
});

$('.navbar-nav > form > .search').on('focus', function(){
  $(this).next('button').removeClass('d-none');
});

$('.navbar-nav > form > .search').on('blur', function(){
  if(!searchHovered) {
       $(this).next('button').addClass('d-none');
  }
  else {
      $(".navbar-nav > form > .search").bind("mouseup",function() {
           $('.navbar-nav > form > button').addClass('d-none');
      })
  }
})

$('.nav-item > a.notification').on('click', function () {
  let pending = parseInt($('#notification-icon').attr('data-count'));
  if( pending > 0){
      $("#notifcation-dropdown").html(
        '<div class="dropdown-item text-center" ><i class="fa fa-spinner fa-spin fa-3x fa-fw"></i></div>'
      );
      const request = new XMLHttpRequest();
      const requestType = 'GET';

      request.open(requestType, `/notifications`);
      request.setRequestHeader("Content-Type", "application/json");
      if (!csrfSafeMethod(requestType) && !this.crossDomain) {
          request.setRequestHeader("X-CSRFToken", csrftoken);
      }
      // Callback function for when request completes
      request.onload = () => {
        const info = JSON.parse(request.responseText);
        const notifcations = notifications_template({"notifications":info})
        $("#notifcation-dropdown").html(notifcations);
        $('#notification-icon').removeAttr('data-count')

      }
      request.send();
  }else{
    $("#notifcation-dropdown").html('<div class="dropdown-item text-center" >No Notifications</div>');
  }

});


$('div[data-href]').on('click', function(){
  let href = $(this).data('href');
  console.log($('.card-text > p').hasClass('collapsing'))
  if (href.match(/^\/(movie|tv)\/(\d+)$/)){
    window.location = href;
  }
});


if ( $('#notification-icon').length > 0 ){
  const requestIcon = new XMLHttpRequest();
  const requestType = 'GET';

  requestIcon.open(requestType, `/notifications-count`);
  requestIcon.setRequestHeader("Content-Type", "application/json");
  if (!csrfSafeMethod(requestType) && !this.crossDomain) {
      requestIcon.setRequestHeader("X-CSRFToken", csrftoken);
  }
  // Callback function for when request completes
  requestIcon.onload = () => {
    const info = JSON.parse(requestIcon.responseText);
    if ( info['count'] > 0 ){
      $('#notification-icon').attr('data-count',info['count'])
    }
  }
  requestIcon.send();
}
