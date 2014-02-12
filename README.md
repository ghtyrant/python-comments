python-comments
===============

Small replacement for e.g. Disqus for implementing comment systems on static websites.

For a demo, visit http://skyr.at.

JavaScript
----------

The following example shows how it can be used:

```javascript
<div id="comments-display"></div>
<form id="comment-form" method="POST" action="#">
  <input type="text" name="username"/>
  <textarea name="text"></textarea>
  <input type="button" id="submit" value="Post"/>
  <input type="hidden" name="id" value="<YOUR ARTICLE ID>"/>
</form>

<script type="text/javascript">
  function load_comments(id)
  {
    $.get("http://skyr.at/comments/get/" + id, function(data) {
          var target = $('#comments-display');
          target.empty();

          $(data.comments).each(function(index, comment) {
            comment_div = document.createElement('div');
            $(comment_div).append($(document.createElement('h2')).text(comment.username + ", " + comment.date_posted));
            $(comment_div).append($(document.createElement('p')).text(comment.text));

            $(target).append(comment_div);
          });
        },
        'json');
  }

  $(document).ready(function() {
      load_comments("<YOUR ARTICLE ID>");
      $('#submit').click( function() {
        $.post("http://skyr.at/comments/add", $('form#comment-form').serialize(), function(data) {
            load_comments("<YOUR ARTICLE ID>");
          });
      });
  });
</script>
