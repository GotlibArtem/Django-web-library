$(document).ready(function() {
    $('#give-book').click(function() {
      $.ajax({
        url: '/give_fiction_book/',
        type: 'POST',
        data: {
          'csrfmiddlewaretoken': '{{ csrf_token }}',
          'issued_books': {
            'book_id': 'book-id',
            'book_name': 'book_name'
          }
        },
        success: function(data) {
          $('#issued-books').html(data);
        }
      });
    });
  });