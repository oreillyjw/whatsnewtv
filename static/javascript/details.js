$("#new-star-rating").rating({
  starCaptions: function(val) {
      return `${val} Stars`
  },
  starCaptionClasses: function(val) {
    return "";
  },
  size: 'sm'
});

$('.existing-rating').rating({
  starCaptions: function(val) {
      return `${val} Stars`
  },
  starCaptionClasses: function(val) {
    return "";
  },
  size: 'xs',
  displayOnly: true
});

$('.heart-circle').on('click', function(){
  data = {
      favorited: !$(this).data('favorited'),
      type: $(this).data('type'),
      id: $(this).data('id')
  };
  const request = new XMLHttpRequest();
  const requestType = 'POST';

  request.open(requestType, `/favorite`);
  request.setRequestHeader("Content-Type", "application/json");

  if (!csrfSafeMethod(requestType) && !this.crossDomain) {
      request.setRequestHeader("X-CSRFToken", csrftoken);
  }
  // Callback function for when request completes
  request.onload = () => {
    const info = JSON.parse(request.responseText);
    let favoriteData = 0,
        $heartDiv = $('.heart-circle');

    if(info['favorited'] === "true"){
      $heartDiv.addClass('favorited');
      favoriteData = 1;
    }else{
      $heartDiv.removeClass('favorited');
    }

    $heartDiv.data('favorited', favoriteData);

  }
  request.send(JSON.stringify(data));
});

//https://www.algolia.com/doc/tutorials/search-ui/autocomplete/autocomplete-textarea/
var lastQuery = '';
$('#commentTextarea').textcomplete([
  {
    // #3 - Regular expression used to trigger the autocomplete dropdown
    match: /(^|\s)@(\w*(?:\w*))$/,
    // #4 - Function called at every new keystroke
    search: function(query, callback) {
      const request = new XMLHttpRequest();
      const requestType = 'POST';
      let data = {
        "query": query,
      };

      request.open(requestType, `/followers`);
      request.setRequestHeader("Content-Type", "application/json");

      if (!csrfSafeMethod(requestType) && !this.crossDomain) {
          request.setRequestHeader("X-CSRFToken", csrftoken);
      }
      // Callback function for when request completes
      request.onload = () => {
        const info = JSON.parse(request.responseText);
        callback(info);
      }
      request.send(JSON.stringify(data));
      lastQuery = query;
    },
    // #5 - Template used to display each result obtained by the Algolia API
    template: function (hit) {
      console.log(hit)
      // Returns the highlighted version of the name attribute
      return `${hit.username}`;
    },
    // #6 - Template used to display the selected result in the textarea
    replace: function (hit) {
      var html = ` @${hit.username} `;

      return html;
    }
  }
]);
