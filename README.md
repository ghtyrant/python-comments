python-comments
===============

Small replacement for e.g. Disqus for implementing comment systems on static websites.
It also offers standard captchas. To generate one, start a GET request to /captcha, which will return an ID. To display it, use `http://yourserver/get_captcha/<ID>`.
When POSTing the comment, include the user's input as a field called "captcha" and the ID in a hidden field called "captcha_id".

For a demo, visit http://skyr.at.

JavaScript
----------

The following example shows how it can be used:

```javascript
<div id="comments-display"></div>
<form id="comment-form" method="POST" action="#">
  <input type="text" name="username"/>
  <img id="captcha_img" src=""><br/>
  <input type="text" name="captcha"/>
  <input type="hidden" id="captcha_id" name="captcha_id"/>
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

  function load_captcha()
  {
    $.get("http://skyr.at/comments/captcha", function(data) {
      $('#captcha_img').attr('src', "http://skyr.at/comments/get_captcha/" + data.id);
      $('#captcha_id').attr('value', data.id);
    },
    'json');
  }


  $(document).ready(function() {
      load_comments("<YOUR ARTICLE ID>");
      load_captcha();
      $('#submit').click( function() {
        $.post("http://skyr.at/comments/add", $('form#comment-form').serialize(), function(data) {
            if (!data.success) {
              alert("Wrong captcha!");
              load_captcha();
            }
            else
              load_comments("<YOUR ARTICLE ID>");
          },
          'json');
      });
  });
</script>
